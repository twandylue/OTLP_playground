from random import randint
from flask import Flask, request
import logging
from opentelemetry import trace

trace = trace.get_tracer("dice-roller.tracer")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    return str(roll())


def roll():
    with trace.start_as_current_span("roll") as rollspan:
        res = randint(1, 6)
        rollspan.set_attribute("roll.value", res)
        say_hi()
        return res


def say_hi():
    with trace.start_as_current_span("say_hi") as hispan:
        hispan.set_attribute("say_hi.value", "Hello")
        return "Hello"
