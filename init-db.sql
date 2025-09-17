-- Initialize KMRL Document AI Database
-- This script runs when the PostgreSQL container starts for the first time

-- Enable UUID extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create any additional extensions or initial data here
-- The main schema will be created by Alembic migrations
