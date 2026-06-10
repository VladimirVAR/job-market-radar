{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
      Keep dbt model schemas aligned with the project architecture.

      Default dbt behavior combines target.schema and custom schema names
      (for example public_staging). For this local dbt project, we want
      models configured with +schema: staging/warehouse/marts to be created
      directly in those PostgreSQL schemas.
    #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
