Inspired by https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f


Want:
 - Escalated responses from human experts => stored as authoritative
 - FAQ accumulation

Maybe:
 - Answers summarized from product code => stored with reference to sources

Not want:
 - Re-summarize existing documentation into wiki (not job of a support bot)


## Files

/support/summary
/support/wiki/index
/support/wiki/faq-this-topic
/support/wiki/faq-that-topic
/support/wiki/20260412-escalated-this-question
/support/wiki/20260413-escalated-that-question


How `/support/wiki/index` looks like:

```
/support/wiki/faq-this-topic -- This topic consists of A B and C.
/support/wiki/faq-that-topic -- That covers X Y and Z.
/support/wiki/20260412-escalated-this-question -- Alice explains this question, sets the priorities and despells myths
/support/wiki/20260413-escalated-that-question -- Bob explains that question and gives interpretation of a doc page
```


## Support Procedures

save escalated

update index
