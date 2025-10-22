"""
Simple template engine for CGI application
Python 3.7+ standard library only
"""

import re
import html
from pathlib import Path


class Template:
    """Simple template engine"""
    
    TEMPLATE_DIR = None
    
    def __init__(self, template_name):
        if Template.TEMPLATE_DIR is None:
            raise ValueError("TEMPLATE_DIR not configured")
        
        self.template_path = Path(Template.TEMPLATE_DIR) / template_name
        self.template_content = self._load_template()
    
    def _load_template(self):
        """Load template file"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render(self, **context):
        """Render template with context"""
        content = self.template_content
        
        # Process includes: {% include "filename" %}
        content = self._process_includes(content)
        
        # Process for loops: {% for item in items %}...{% endfor %}
        content = self._process_for_loops(content, context)
        
        # Process if statements: {% if condition %}...{% endif %}
        content = self._process_if_statements(content, context)
        
        # Process variables: {{ variable }}
        content = self._process_variables(content, context)
        
        return content
    
    def _process_includes(self, content):
        """Process {% include "template" %}"""
        pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
        
        def replace_include(match):
            include_name = match.group(1)
            try:
                template = Template(include_name)
                return template.template_content
            except Exception:
                return f'<!-- Include not found: {include_name} -->'
        
        return re.sub(pattern, replace_include, content)
    
    def _process_for_loops(self, content, context):
        """Process {% for item in items %}...{% endfor %}"""
        pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_loop(match):
            item_name = match.group(1)
            items_name = match.group(2)
            loop_content = match.group(3)
            
            items = context.get(items_name, [])
            if not items:
                return ''
            
            result = []
            for i, item in enumerate(items):
                loop_context = context.copy()
                loop_context[item_name] = item
                loop_context['loop'] = {
                    'index': i + 1,
                    'index0': i,
                    'first': i == 0,
                    'last': i == len(items) - 1
                }
                
                rendered = loop_content
                rendered = self._process_if_statements(rendered, loop_context)
                rendered = self._process_variables(rendered, loop_context)
                result.append(rendered)
            
            return ''.join(result)
        
        return re.sub(pattern, replace_loop, content, flags=re.DOTALL)
    
    def _process_if_statements(self, content, context):
        """Process {% if condition %}...{% endif %}"""
        # Simple if without else
        pattern = r'{%\s*if\s+(.+?)\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_if(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            
            # Evaluate condition
            if self._evaluate_condition(condition, context):
                return self._process_variables(if_content, context)
            return ''
        
        return re.sub(pattern, replace_if, content, flags=re.DOTALL)
    
    def _evaluate_condition(self, condition, context):
        """Evaluate condition"""
        # Handle negation: not variable
        if condition.startswith('not '):
            return not self._evaluate_condition(condition[4:].strip(), context)
        
        # Handle comparison: var == 'value'
        if '==' in condition:
            left, right = [x.strip() for x in condition.split('==', 1)]
            left_val = self._get_value(left, context)
            right_val = self._get_value(right, context)
            return left_val == right_val
        
        if '!=' in condition:
            left, right = [x.strip() for x in condition.split('!=', 1)]
            left_val = self._get_value(left, context)
            right_val = self._get_value(right, context)
            return left_val != right_val
        
        # Handle simple variable check
        value = self._get_value(condition, context)
        return bool(value)
    
    def _get_value(self, expr, context):
        """Get value from expression"""
        expr = expr.strip()
        
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        # Number
        try:
            return int(expr)
        except ValueError:
            pass
        
        # Function call: range(1, 10)
        if '(' in expr and expr.endswith(')'):
            func_name = expr[:expr.index('(')]
            if func_name == 'range':
                args_str = expr[expr.index('(')+1:-1]
                args = [int(x.strip()) for x in args_str.split(',')]
                return list(range(*args))
        
        # Variable with dot notation: user.name
        parts = expr.split('.')
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            
            if value is None:
                return None
        
        return value
    
    def _process_variables(self, content, context):
        """Process {{ variable }}"""
        pattern = r'{{\s*([^}]+)\s*}}'
        
        def replace_var(match):
            var_expr = match.group(1).strip()
            
            # Handle filters: variable|filter
            if '|' in var_expr:
                var_name, filters = var_expr.split('|', 1)
                var_name = var_name.strip()
                value = self._get_value(var_name, context)
                
                # Apply filters
                for filter_name in filters.split('|'):
                    filter_name = filter_name.strip()
                    value = self._apply_filter(filter_name, value, context)
                
                return str(value) if value is not None else ''
            
            value = self._get_value(var_expr, context)
            
            # Auto-escape HTML
            if value is not None:
                return html.escape(str(value))
            return ''
        
        return re.sub(pattern, replace_var, content)
    
    def _apply_filter(self, filter_name, value, context):
        """Apply template filter"""
        if filter_name == 'safe':
            return value  # Don't escape
        elif filter_name == 'length':
            return len(value) if value else 0
        elif filter_name == 'upper':
            return str(value).upper() if value else ''
        elif filter_name == 'lower':
            return str(value).lower() if value else ''
        elif filter_name.startswith('default:'):
            default = filter_name.split(':', 1)[1].strip('"\'')
            return value if value else default
        
        return value


def render_template(template_name, **context):
    """Helper function to render template"""
    template = Template(template_name)
    return template.render(**context)
