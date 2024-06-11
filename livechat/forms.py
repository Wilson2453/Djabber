from django import forms
from django.utils.text import slugify
from .models import User, Room, Message

class RoomCreationForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Room
        fields = ['name', 'members']

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].queryset = User.objects.exclude(id=owner.id)

    def save(self, commit=True):
        room = super().save(commit=False)
        room.slug = slugify(room.name)
        if commit:
            room.save()
            self.save_members()
        return room

    def save_members(self):
        # Clear existing members and add selected members to the room
        self.instance.members.clear()
        self.instance.members.add(*self.cleaned_data['members'])
        # Add the owner to the members list
        self.instance.members.add(self.instance.owner)