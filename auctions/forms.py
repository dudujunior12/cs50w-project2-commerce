from django import forms


choices = [(None, 'Select a category (Optional)'), ('Home', 'Home'), ('Eletronics', 'Eletronics'), ('Fashion', 'Fashion'), ('Toys', 'Toys')]


class CreateListing(forms.Form):
	title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Title', 'class':'form-control'}))
	description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description', 'class':'form-control', 'rows': '5'}))
	start_bid = forms.DecimalField(max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Start Bid', 'class':'form-control'}))
	category = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class':'form-control'}))
	image_url = forms.URLField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Image List Url (Optional)', 'class':'form-control'}))

class CreateBid(forms.Form):
	bid_value = forms.DecimalField(max_digits=5, decimal_places=2, label='', widget=forms.NumberInput(attrs={'placeholder': 'Bid', 'class':'form-control'}))

class CreateComment(forms.Form):
	comment = forms.CharField(label='', widget=forms.Textarea(attrs={'placeholder': 'Comment', 'class':'form-control', 'rows': '5'}))
	


