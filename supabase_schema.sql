-- ============================================================================
-- 🌊 BasinShift: FloodCast Disaster Intelligence Platform
-- Supabase PostgreSQL Schema Definition
-- Project ID: kgdyupauslkdqojqcwkw
-- ============================================================================

-- 0. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. CATCHMENTS / BASINS TABLE
-- Stores metadata, geography, and flood threshold parameters
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.catchments (
    id TEXT PRIMARY KEY,                                      -- e.g. 'camels_05503800' or 'BASIN_001'
    name TEXT NOT NULL,
    country TEXT DEFAULT 'USA',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    drainage_area_km2 DOUBLE PRECISION,
    safe_discharge_threshold DOUBLE PRECISION DEFAULT 15.0,  -- m3/s safe flow ceiling
    critical_discharge_threshold DOUBLE PRECISION DEFAULT 30.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. HISTORICAL TELEMETRY TABLE
-- Time-series daily hydrological data (Precipitation, Soil Moisture, Observed Flow)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.historical_telemetry (
    id BIGSERIAL PRIMARY KEY,
    catchment_id TEXT NOT NULL REFERENCES public.catchments(id) ON DELETE CASCADE,
    recorded_date DATE NOT NULL,
    observed_discharge DOUBLE PRECISION,                     -- Actual river flow (m3/s)
    precipitation DOUBLE PRECISION,                          -- mm/day
    soil_moisture DOUBLE PRECISION,                          -- volumetric index
    temperature DOUBLE PRECISION,                            -- deg C
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_catchment_date UNIQUE(catchment_id, recorded_date)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_catchment_date 
ON public.historical_telemetry(catchment_id, recorded_date DESC);

-- ============================================================================
-- 3. MODEL FORECASTS TABLE
-- Output predictions directly generated from PyTorch LSTM / FLOODCAST.ipynb
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.model_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    catchment_id TEXT NOT NULL REFERENCES public.catchments(id) ON DELETE CASCADE,
    forecast_origin TIMESTAMPTZ NOT NULL,                    -- The forecast origin horizon (T0)
    model_version TEXT DEFAULT 'PyTorch-LSTM-v1',
    horizons_days INTEGER[] NOT NULL,                        -- ARRAY[1, 3, 7]
    predicted_discharge DOUBLE PRECISION[] NOT NULL,         -- ARRAY[12.4, 14.1, 18.7]
    high_flow_probability DOUBLE PRECISION[] NOT NULL,       -- Flow probability estimates
    extreme_flow_probability DOUBLE PRECISION[] NOT NULL,
    lower_bound DOUBLE PRECISION[] NOT NULL,                 -- 90% Confidence Interval Lower Bound
    upper_bound DOUBLE PRECISION[] NOT NULL,                 -- 90% Confidence Interval Upper Bound
    raw_schema_payload JSONB,                                -- Full JSON schema payload from notebook
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_catchment_origin 
ON public.model_forecasts(catchment_id, forecast_origin DESC);

-- ============================================================================
-- 4. FLOOD ALERTS & DIRECTIVES TABLE
-- Automated warning directives, severity breach tracking, and operator acknowledgements
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.flood_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    catchment_id TEXT NOT NULL REFERENCES public.catchments(id) ON DELETE CASCADE,
    forecast_id UUID REFERENCES public.model_forecasts(id) ON DELETE CASCADE,
    severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    peak_discharge DOUBLE PRECISION NOT NULL,
    breach_percentage DOUBLE PRECISION NOT NULL,
    alert_heading TEXT NOT NULL,
    alert_body TEXT NOT NULL,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_active 
ON public.flood_alerts(catchment_id, is_acknowledged, created_at DESC);

-- ============================================================================
-- 5. MODEL EXPERIMENTS & LAB METRICS TABLE
-- Tracks Colab training checkpoints, RMSE/MAE metrics, and Huber Loss parameters
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.model_experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL,                                -- 'PyTorch-LSTM' or 'LightGBM-RegAlpha'
    test_rmse DOUBLE PRECISION NOT NULL,                     -- 2.49 m3/s
    test_mae DOUBLE PRECISION NOT NULL,                      -- 0.76 m3/s
    loss_function TEXT DEFAULT 'Huber Loss',
    sequence_length INTEGER DEFAULT 365,
    hyperparameters JSONB,
    weights_path TEXT,                                       -- 'flood_lstm_weights.pth'
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. COPILOT CHAT MESSAGES TABLE
-- Persistent conversation logs and telemetry grounding for Groq AI Copilot
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.copilot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    catchment_id TEXT REFERENCES public.catchments(id) ON DELETE SET NULL,
    user_prompt TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    telemetry_grounding JSONB,                               -- Contextual snapshot passed to Groq LLM
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_copilot_session 
ON public.copilot_messages(session_id, created_at ASC);

-- ============================================================================
-- 7. REALTIME PUBLICATION SETUP
-- Publish tables to Supabase Realtime websocket engine
-- ============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE public.catchments;
ALTER PUBLICATION supabase_realtime ADD TABLE public.model_forecasts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.flood_alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.copilot_messages;

-- ============================================================================
-- 8. AUTOMATIC ALERT TRIGGER FUNCTION
-- Automatically generates a flood_alert whenever a forecast exceeds safe threshold
-- ============================================================================
CREATE OR REPLACE FUNCTION public.fn_evaluate_flood_forecast()
RETURNS TRIGGER AS $$
DECLARE
    v_safe_threshold DOUBLE PRECISION;
    v_max_pred DOUBLE PRECISION;
    v_breach_pct DOUBLE PRECISION;
    v_severity TEXT;
    v_high_prob DOUBLE PRECISION := 0.0;
BEGIN
    -- Fetch safe limit configured for this catchment
    SELECT safe_discharge_threshold INTO v_safe_threshold
    FROM public.catchments WHERE id = NEW.catchment_id;

    IF v_safe_threshold IS NULL THEN
        v_safe_threshold := 15.0;
    END IF;

    -- Calculate peak predicted discharge across all horizons
    SELECT MAX(val) INTO v_max_pred FROM UNNEST(NEW.predicted_discharge) AS val;

    IF v_max_pred > v_safe_threshold THEN
        v_breach_pct := ROUND(((v_max_pred - v_safe_threshold) / v_safe_threshold * 100.0)::numeric, 1);
        
        IF v_breach_pct > 50.0 THEN
            v_severity := 'CRITICAL';
        ELSIF v_breach_pct > 20.0 THEN
            v_severity := 'HIGH';
        ELSE
            v_severity := 'MODERATE';
        END IF;

        IF array_length(NEW.high_flow_probability, 1) > 0 THEN
            v_high_prob := ROUND((NEW.high_flow_probability[array_length(NEW.high_flow_probability, 1)] * 100.0)::numeric, 1);
        END IF;

        INSERT INTO public.flood_alerts (
            catchment_id,
            forecast_id,
            severity,
            peak_discharge,
            breach_percentage,
            alert_heading,
            alert_body
        ) VALUES (
            NEW.catchment_id,
            NEW.id,
            v_severity,
            v_max_pred,
            v_breach_pct,
            v_severity || ' FLOOD RISK ALERT — Projected peak discharge crosses ' || v_safe_threshold || ' m³/s threshold',
            'Model projection reaches ' || v_max_pred || ' m³/s (+' || v_breach_pct || '% breach). High Flow Probability: ' || v_high_prob || '%.'
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_evaluate_forecast ON public.model_forecasts;
CREATE TRIGGER trg_evaluate_forecast
AFTER INSERT ON public.model_forecasts
FOR EACH ROW
EXECUTE FUNCTION public.fn_evaluate_flood_forecast();

-- ============================================================================
-- 9. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
ALTER TABLE public.catchments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historical_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flood_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.copilot_messages ENABLE ROW LEVEL SECURITY;

-- Frontend Read-Only Policies (Accessible with anon key)
DROP POLICY IF EXISTS "Public Read Catchments" ON public.catchments;
CREATE POLICY "Public Read Catchments" ON public.catchments FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public Read Telemetry" ON public.historical_telemetry;
CREATE POLICY "Public Read Telemetry" ON public.historical_telemetry FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public Read Forecasts" ON public.model_forecasts;
CREATE POLICY "Public Read Forecasts" ON public.model_forecasts FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public Read Alerts" ON public.flood_alerts;
CREATE POLICY "Public Read Alerts" ON public.flood_alerts FOR SELECT USING (true);

-- Frontend Operator Interactivity (Acknowledge alert & Send Copilot chat)
DROP POLICY IF EXISTS "Public Acknowledge Alerts" ON public.flood_alerts;
CREATE POLICY "Public Acknowledge Alerts" ON public.flood_alerts FOR UPDATE USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public Read & Insert Copilot Messages" ON public.copilot_messages;
CREATE POLICY "Public Read & Insert Copilot Messages" ON public.copilot_messages FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Public Read Experiments" ON public.model_experiments;
CREATE POLICY "Public Read Experiments" ON public.model_experiments FOR SELECT USING (true);

-- Note: The service_role secret key automatically bypasses RLS for full write/insert/update access!

