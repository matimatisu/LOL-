# gacha/forms.py
from django import forms

class FiveSummonerForm(forms.Form):
    summoner1 = forms.CharField(label="サモナーネーム", max_length=30,
                                widget=forms.TextInput(attrs={"placeholder": "例: Dran"}))
    summoner2 = forms.CharField(label="サモナーネーム", max_length=30,
                                widget=forms.TextInput(attrs={"placeholder": "例: Orner"}))
    summoner3 = forms.CharField(label="サモナーネーム", max_length=30,
                                widget=forms.TextInput(attrs={"placeholder": "例: Faker"}))
    summoner4 = forms.CharField(label="サモナーネーム", max_length=30,
                                widget=forms.TextInput(attrs={"placeholder": "例: Gumayusi"}))
    summoner5 = forms.CharField(label="サモナーネーム", max_length=30,
                                widget=forms.TextInput(attrs={"placeholder": "例: Keria"}))
    
    exclude_yuumi = forms.BooleanField(
        label = "ユーミを除外する",
        required = False,
    )