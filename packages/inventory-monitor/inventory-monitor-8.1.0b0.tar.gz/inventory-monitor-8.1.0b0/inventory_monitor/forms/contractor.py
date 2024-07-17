from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField, TagFilterField

from inventory_monitor.models import Contractor


class ContractorForm(NetBoxModelForm):
    comments = CommentField(label="Comments")

    class Meta:
        model = Contractor
        fields = ("name", "company", "address", "tags", "comments", "tags")


class ContractorFilterForm(NetBoxModelFilterSetForm):
    model = Contractor
    tag = TagFilterField(model)
    name = forms.CharField(required=False)
    company = forms.CharField(required=False)
    address = forms.CharField(required=False)
