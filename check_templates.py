#!/usr/bin/env python
import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

# Check all templates
templates = ['base.html', 'index.html', 'projects.html', 'project.html']

for template_name in templates:
    try:
        template = env.get_template(template_name)
        print(f"✓ {template_name} - OK")
    except TemplateSyntaxError as e:
        print(f"✗ {template_name} - ERROR on line {e.lineno}:")
        print(f"  {e.message}")
    except Exception as e:
        print(f"✗ {template_name} - ERROR: {e}")
