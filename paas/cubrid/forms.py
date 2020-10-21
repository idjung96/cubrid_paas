from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import Form, CharField, TextInput, PasswordInput, ChoiceField, BooleanField


# STATES = (
#     ('', '선택하기'),
#     ('kr', '대한민국'),
#     ('jp', '일본'),
# )


class CUBRIDBuildForm(forms.Form):
    SERVER_TYPE = (
        ('', '선택'),
        ('S4-G2', 'Standard-4 CPU-16GB RAM'),
        ('S8-G2', 'Standard-8 CPU-32GB RAM'),
        ('S16-G2', 'Standard-16 CPU-64GB RAM'),
        ('M4-G2', 'HighMem 4CPU-32GB RAM'),
        ('M8-G2', 'HighMem 8 CPU-64GB RAM'),
        ('M16-G2', 'HighMem 16 CPU-128GB RAM'),
    )
    HA_TYPE = (
        ('single', '1 Instance'),
        ('1standby', 'Active-Standby'),
        ('2standby', 'Active-Standby-Standby'),
        ('1replica', 'Active-Standby-Replica'),
        ('2replica', 'Active-Standby-Replica-Replica'),
    )
    cluster_name = CharField(
        widget=TextInput(
            attrs={'placeholder': 'Cluster Name'}))
    # password = CharField(
    #     widget=PasswordInput()
    # )
    server_type = ChoiceField(choices=SERVER_TYPE)
    ha_type = ChoiceField(choices=HA_TYPE)
    pc_ip = CharField(
        label='PC(DBA) IP Address. Use Separator(;) if num(PC) > 2',
        widget=TextInput(
            attrs={'placeholder': '-'}), required=False)
    was_ip = CharField(
        label='WAS IP Address. Use Separator(;) if num(WAS) > 2',
        initial='*',
        widget=TextInput(
            attrs={'placeholder': 'Separator(;)'}), required=False)
    # check_me_out = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('cluster_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ha_type', css_class='form-group col-md-6 mb-0'),
                Column('server_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('pc_ip', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('was_ip', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            # 'check_me_out',
            Submit('submit', 'Build')
        )
