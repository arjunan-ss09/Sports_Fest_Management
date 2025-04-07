from django import forms
from .models import Match, Event, Team, ParticipantProfile, Feedback

class ParticipantRegistrationForm(forms.ModelForm):
    college = forms.CharField(max_length=255, required=True, label="College")
    class Meta:
        model = ParticipantProfile
        fields = ['name', 'gender', 'date_of_birth', 'mobile_number', 'email',]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
SPORT_SCORE_FIELDS = {
    "Cricket": [
        ("team1_runs", "Team 1 Runs", forms.IntegerField(min_value=0, required=False)),
        ("team1_wickets", "Team 1 Wickets", forms.IntegerField(min_value=0, required=False)),
        ("team2_runs", "Team 2 Runs", forms.IntegerField(min_value=0, required=False)),
        ("team2_wickets", "Team 2 Wickets", forms.IntegerField(min_value=0, required=False)),
        ("result", "Result", forms.ChoiceField(
            choices=[("Team1", "Team 1 Win"), ("Team2", "Team 2 Win"), ("Draw", "Draw")],
            required=False
        )),
    ],
    "Football": [
        ("team1_goals", "Team 1 Goals", forms.IntegerField(min_value=0, required=False)),
        ("team2_goals", "Team 2 Goals", forms.IntegerField(min_value=0, required=False)),
        ("result", "Result", forms.ChoiceField(
            choices=[("Team1", "Team 1 Win"), ("Team2", "Team 2 Win"), ("Draw", "Draw")],
            required=False
        )),
    ],
    "Athletics": [
        ("results", "Results:", forms.CharField(
            widget=forms.Textarea,
            required=False,
        )),
    ],
    "Table Tennis": [
        ("team1_sets", "Team 1 Sets Won", forms.IntegerField(min_value=0, required=False)),
        ("team2_sets", "Team 2 Sets Won", forms.IntegerField(min_value=0, required=False)),
        ("result", "Result", forms.ChoiceField(
            choices=[("Team1", "Team 1 Win"), ("Team2", "Team 2 Win")],
            required=False
        )),
    ],
}

class ScoreForm(forms.Form):
    finished = forms.BooleanField(
        required=False,
        label="Mark as Finished",
        help_text="Check if this match is finished."
    )

    def __init__(self, sport, *args, **kwargs):
        """
        Initialize the form dynamically with fields based on the sport.
        """
        super().__init__(*args, **kwargs)
        fields_for_sport = SPORT_SCORE_FIELDS.get(sport, [])
        for field_name, label, field_instance in fields_for_sport:
            field_instance.label = label
            self.fields[field_name] = field_instance

SPORT_MAX_TEAMS = {
    'Cricket': 2,
    'Football': 2,
    'Table Tennis': 2,
    'Athletics': 8,
}

class MatchForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Enter the match start time."
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Enter the match end time."
    )
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Teams"
    )

    class Meta:
        model = Match
        fields = ['event', 'start_time', 'end_time', 'teams']

    def __init__(self, *args, **kwargs):
        step = kwargs.pop('step', 1)
        extra_event_id = kwargs.pop('extra_event_id', None)
        super().__init__(*args, **kwargs)
        
        if step == 1:
            if 'teams' in self.fields:
                del self.fields['teams']
        else:
            if 'teams' not in self.fields:
                self.fields['teams'] = forms.ModelMultipleChoiceField(
                    queryset=Team.objects.none(),
                    widget=forms.CheckboxSelectMultiple,
                    required=True,
                    label="Select Teams"
                )
            event = None
            if extra_event_id:
                try:
                    event = Event.objects.get(id=extra_event_id)
                except Event.DoesNotExist:
                    pass
            elif self.data.get('event'):
                try:
                    event = Event.objects.get(id=self.data.get('event'))
                except (ValueError, Event.DoesNotExist):
                    pass
            elif self.instance.pk and self.instance.event:
                event = self.instance.event

            if event:
                self.fields['teams'].queryset = Team.objects.filter(event=event)
            else:
                self.fields['teams'].queryset = Team.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        teams = cleaned_data.get('teams')
        if event and teams is not None:
            allowed = SPORT_MAX_TEAMS.get(event.sport, 2)
            if event.sport=='Athletics':
                if len(teams) > allowed:
                    raise forms.ValidationError(
                    f"For {event.sport} matches, please select exactly {allowed} teams.")
            else:
                if len(teams)!= allowed:
                    raise forms.ValidationError(
                    f"For {event.sport} matches, please select exactly {allowed} teams.")
            for team in teams:
                if team.event != event:
                    raise forms.ValidationError(f"Team '{team}' does not belong to the selected event.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if 'teams' in self.cleaned_data:
            instance.teams.set(self.cleaned_data.get('teams'))
        if commit:
            instance.save()
        return instance



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message', 'image']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your feedback here...'}),
        }