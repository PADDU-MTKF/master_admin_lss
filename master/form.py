from django import forms

class YourForm(forms.Form):

    def __init__(self, attr_list=None,default_data=None, *args, **kwargs):
        super(YourForm, self).__init__(*args, **kwargs)
        if attr_list:
        
            for field_dict in attr_list:  # Iterate over each dictionary in the list
               
            
                column_name = field_dict.get('column_name').replace('_', ' ')  # Access the dictionary using string keys
                column_type = field_dict.get('column_type')
                required = field_dict.get('required')
                fld_size = field_dict.get('size') if field_dict.get('size')!=0 else None
                default = default_data[column_name] if default_data else field_dict.get('default')
                
              
                
                
                
            
              
                is_image = 'image' in column_name.lower()
                
                if is_image:
                    self.fields[column_name] = forms.ImageField(
                        label=column_name,
                        required=required,
                        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control-file'})
                    )
                
                elif column_type == 'string':
                    if fld_size is not None and fld_size>=20:
                        widget = forms.Textarea(attrs={'class': 'form-control-area'})  # Use Textarea widget
                    else:
                        widget = forms.TextInput(attrs={'class': 'form-control'})  # Use TextInput widget
        
                        
                    self.fields[column_name] = forms.CharField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=widget,
                        max_length=fld_size
                    )
                    
                elif column_type == 'integer':
                    self.fields[column_name] = forms.IntegerField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif column_type == 'double':
                    self.fields[column_name] = forms.DecimalField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
                    )
                elif column_type == 'boolean':
                    self.fields[column_name] = forms.BooleanField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
                elif column_type == 'datetime':
                    self.fields[column_name] = forms.DateTimeField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.DateTimeInput(attrs={'class': 'form-control datepicker'})
                    ) 
                elif column_type == 'email':
                    self.fields[column_name] = forms.EmailField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.EmailInput(attrs={'class': 'form-control'})
                    )
                elif column_type == 'ip':
                    self.fields[column_name] = forms.CharField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b'})
                    )
                elif column_type == 'url':
                    self.fields[column_name] = forms.URLField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.URLInput(attrs={'class': 'form-control'})
                    )
                elif column_type == 'url_list':
                    self.fields[column_name] = forms.CharField(
                        label=column_name,
                        required=required,
                        initial=default,
                        widget=forms.Textarea(attrs={'class': 'form-control'})
                    )

