## pinboard\_queue

A Pinboard.in feed to Message Queue doer

### Installation

    $ pip install .


### Design

* What is the idempotency? datetime + hash?
  * hash is an md5 of the URL. hash doesn't change when metadata is updated (tags, description etc)
* Where to store idempotency?
* Is it OK to send URLs out of order?
* How should we rate limit? https://pinboard.in/api#limits
