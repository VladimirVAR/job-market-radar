-- ============================================================
-- Job Market Radar
-- Task 003: Create Raw Schema
-- File: sql/ddl/001_create_schemas.sql
--
-- Purpose:
--   Create project schemas used by the layered architecture:
--   raw -> staging -> warehouse -> marts
-- ============================================================

create extension if not exists pgcrypto;

create schema if not exists raw;
create schema if not exists staging;
create schema if not exists warehouse;
create schema if not exists marts;