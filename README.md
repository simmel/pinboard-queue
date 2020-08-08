## pinboard\_queue

A Pinboard.in feed to Message Queue doer

### Build

    $ rebar3 compile


### Design

* What is the idempotency? datetime + hash?
  * hash is an md5 of the URL. hash doesn't change when metadata is updated (tags, description etc)
* Where to store idempotency?
* Is it OK to send URLs out of order?
* How should we rate limit? https://pinboard.in/api#limits


```

   /          \
rss_sup    mq_sup
   |           |
 worker      worker

```
