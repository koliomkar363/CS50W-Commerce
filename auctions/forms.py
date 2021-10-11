from django import forms


class CreateListingForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={
            "style": "width: 600px"
        }
    ))
    description = forms.CharField(label="", widget=forms.Textarea(
        attrs={
            "placeholder": "Description",
            "style": "height: 150px; width: 637px"
        }
    ))
    bid = forms.DecimalField(min_value=0.1, decimal_places=2)
    image_url = forms.CharField(required=False, widget=forms.URLInput(
        attrs={
            "placeholder": "Paste your image url here",
            "style": "width: 565px"
        }
    ))


class AddCommentForm(forms.Form):
    comment = forms.CharField(label="", required=False, widget=forms.Textarea(
        attrs={
            "placeholder": "Add your comment here",
            "style": "height:100px"
        }
    ))
