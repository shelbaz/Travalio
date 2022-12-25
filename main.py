from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms import validators
import openai
import os

app = Flask(__name__)
app.template_folder = 'templates'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config[
  'SECRET_KEY'] = '\x0b\x8d\x0f\xb1\xff\xa5l+Sq\xb4.7`S\xb9f\xa0\x8b\\^\xb7\xb5]'

# Initialize the sessiaon
Session(app)


# Set up the questionnaire form
class ItineraryForm(FlaskForm):
  destination = StringField(
    'Destination',
    # choices=[('Paris', 'Paris'), ('New York', 'New York'),
    #          ('London', 'London'), ('Amsterdam', 'Amsterdam'),
    #          ('Barcelona', 'Barcelona'), ('Berlin', 'Berlin'),
    #          ('Budapest', 'Budapest'), ('Copenhagen', 'Copenhagen'),
    #          ('Dubai', 'Dubai'), ('Istanbul', 'Istanbul'), ('Rome', 'Rome'),
    #          ('Venice', 'Venice'), ('Vienna', 'Vienna'), ('Zurich', 'Zurich'),
    #          ('Athens', 'Athens'), ('Edinburgh', 'Edinburgh'),
    #          ('Dublin', 'Dublin'), ('Lisbon', 'Lisbon'), ('Prague', 'Prague'),
    #          ('Madrid', 'Madrid'), ('Munich', 'Munich'),
    #          ('Stockholm', 'Stockholm'), ('Sydney', 'Sydney'),
    #          ('Toronto', 'Toronto'), ('Vancouver', 'Vancouver'),
    #          ('Victoria', 'Victoria'), ('Whistler', 'Whistler'),
    #          ('Florence', 'Florence'), ('Santorini', 'Santorini'),
    #          ('Seville', 'Seville')],
    default='New York',  # Set the default value
    validators=[validators.DataRequired()])
  duration = IntegerField(
    'Duration (days)',
    default=7,  # Set the default value
    validators=[validators.DataRequired(),
                validators.NumberRange(min=1)])
  budget = IntegerField(
    'Budget (USD)',
    default=1000,  # Set the default value
    validators=[validators.DataRequired(),
                validators.NumberRange(min=0)])
  accommodation = SelectField('Accommodation',
                              choices=[('Hotel', 'Hotel'),
                                       ('Airbnb', 'Airbnb'),
                                      ('Backpacking', 'Backpacking')],
                              validators=[validators.DataRequired()])
  activities = StringField(
    'Activities (comma-separated list)',
    default='Sightseeing, Shopping, Food and Drink'  # Set the default value
  )
  submit = SubmitField('Generate Itinerary')


@app.route('/', methods=['GET', 'POST'])
def index():
  form = ItineraryForm()
  itinerary = ''  # Initialize the itinerary variable
  if request.method == 'POST':
    # Print form data to the console
    itinerary = generate_itinerary(form.destination.data, form.duration.data,
                                   form.budget.data, form.accommodation.data,
                                   form.activities.data)
    form_data = {'data': itinerary}

    # Save the itinerary in a session variable
    session['itinerary'] = itinerary
    print("session it")
    print(session['itinerary'])
    plans= []
    plans= itinerary.split("Day")
    print("plans")
    print(plans)
    # Redirect to the itinerary page
    # return redirect('/trip_plan')
  return render_template('index.html', form=form, itinerary=itinerary)
  # Print the contents of the session dictionary to the console


@app.route('/trip_plan', methods=['GET'])
def itinerary():
  # Retrieve the itinerary from the session variable
  itinerary = session.get('itinerary')
  # Print the itinerary to the console
  print("trip plan page")
  
  print(itinerary)
  return render_template('trip_plan.html', itinerary=itinerary)


# Generate the itinerary using the chat GPT API
def generate_itinerary(destination, duration, budget, accommodation,
                       activities):
  openai.api_key = os.environ['api_key']
  prompt = f"I'm planning a trip and would like to get a detailed itinerary that breaks down the locations I will visit, the number of days I will spend at each location, and the suggested activities to do at each location, including suggestions for food and accommodation. My destination is {destination} and I'll be there for {duration} days. I have a budget of {budget} USD and I'm interested in staying in a {accommodation}. I'd like to do the following activities: {activities}. Can you help me plan the itinerary?"
  model_engine = "text-davinci-003"
  print(prompt)
  response = openai.Completion.create(engine=model_engine,
                                      prompt=prompt,
                                      max_tokens=3000,
                                      temperature=0.7)
  itinerary = response['choices'][0]['text']
  return itinerary


# if __name__ == '__main__':
#   app.run(debug=True)

# Run the application
app.run(host='0.0.0.0', port=81)
