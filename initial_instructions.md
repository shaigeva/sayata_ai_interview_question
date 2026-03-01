# Mission statement
This repository is a base for implementing an interview question for the
company Sayata.
The question checks a bit of coding, basic AI tooling proficiency and
problem solving.
Our first objective is to flesh out a concrete plan that's realistic - a
question that can be done by a medium-strong candidate, and will give us
insight for evaluating them.

The basic idea for the project is that we have several steps of the
candidate building things and problem-solving.
The steps become more complex and "larger" so that it's not practical to
code them by hand.
I don't expect the candidate to necessarily finish everything (maybe
we'll create too many tasks by design).
The setting for the interview is a ~1h question (maybe up to 1.5),
typically on zoom together with the interviwers online.
My intuition for the setup is to have a  skeleton repo that we give the
candidate ahead of time (we'll branch that repo from this repo), together
with telling them something like "you will be asked to implement
endpoints that work with an API" or similar instruction. The idea is that
they can set up their AI tooling however they want - we want the
candidate to work with the tooling that they feel comfortable with.

I think (not sure though) the best thing is to have several tasks (maybe
we'll call them tickets. Small features/bugs), some of them independent
of others, and we tell the candidate about all of them at the same time
(probably in text format - we want them to use AI to analyze the tasks as
well if they want to).
Ideally the candidate will implement multiple tasks concurrently.

# Quetion domain
Sayata is an insurance marketplace.
Users give us details about their business (a Submission).
Sayata sends these details to insurance carriers via their API, and receives insurance Quotes in return.
Some carriers return the quote in the same API call - but some need polling and some return them as webooks.
The quotes can then be binded by another API call.

# Question technical high level
The idea is that the candidate will work on a API server (we're starting with FastAPI - python, and after we have that we'll create a Typescript one).
The server receives requests, works against a "staging carrier API" (which is a local python server that the candidate can run on their own, and will be part of this repo - I think these servers will only have in-memory state, to make things simple).

There is a question mark of whether we're provider a testing harness.
We need to be able to send requests to the server - both for the candidate's tests and for us to be able to evaluate the candidate's work.
A testing hardness can typically either actually send requests to a working server, or use a TestClient (which is my standard approach).
The question mark here is that we want to see if the candidate will take care of that themselves.

We should also provide basic API requests and expected responses so that the candidate can use them to understand the requirements.

# Intuition about the starting point
I'm thinking that the starting point will be a repo with a working server that receives a submission and returns "created".
Then the user can query the created submission, and receive a list of quotes.
Then the user can submit a bind request for a quote, and receive "binded" (the bind request needs to send a bind command to the carrier, of course).

Behind the scenes, there will be a simple carrier simulator - a single type of carrier, and we'll start, say, two instances of it so we will have multiple quotes in the response.

I think a single "test script" that uses python requests to send API calls to the server and check the responses.

Other tech notes:
- no auth - a single hard-coded user scenario
- everything stored in memory.


# Intuition about possible tasks.
- Add need for polling - another carrier which doesn't return the quote immediately, but instead returns a "quote id" and then the candidate needs to implement polling to get the quote details.
- Add retries - a carrier that randomly fails, and the candidate needs to implement retries with backoff.
- Try to find ways that the API can be different for another carrier.
- Try to think of ways where something might go wrong that the candidate needs to figure out by themselves.
- Think of ways where there's no clear "documentation" for how to implement something - they either need to let the AI explore the API request/response, or have the AI need to review the docs. E.g. - "support the new carrier's API" - but the new carrier has a different API and the candidate needs to figure out how to work with it.
