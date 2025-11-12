message = "I want to see a bigger property? do you have one?"
user_content = message.lower()

search_keywords = ["bigger", "want to see a", "do you have"]
scheduling_keywords = ["can i visit", "i want to see it"]

search_matches = [kw for kw in search_keywords if kw in user_content]
scheduling_matches = [kw for kw in scheduling_keywords if kw in user_content]

print("Message:", message)
print("Search matches:", search_matches)
print("Scheduling matches:", scheduling_matches)

if scheduling_matches:
    print("Routes to: scheduling_agent")
elif search_matches:
    print("Routes to: search_agent")
else:
    print("Routes to: property_agent")