You just need to do some adjustments in your table...
For example, for single show subscription I haven't store any data in subscription period, subsciption status in subscription
table and same goes for subscription plan in billing history. So you have go to your design table and uncheck the "NOT NULL"
option.
You may still get an error saying that--- check constraint(ora...) violated. To solve this you need to go to 
Subscription->design table->checks and you will understand the rest.