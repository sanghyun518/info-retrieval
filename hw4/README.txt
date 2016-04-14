TEAM MEMBERS: 
* Sanghyun Choi (schoi60)
* Hyun Joon Cho (hcho34)

Part 1.

Modified 'lwp_parser_two.pl' such that it checks the following criteria:
* Contains link of the form {Base URL}# --> Self-referencing links
* Does NOT contain current domain URL --> Non-local links

Part 2.

Filled in the required functions and added a relevancy function that checks
whether the given link contains keywords like 'contact', 'people', and 'about'
since such link will most likely contain emails, phone numbers, or addresses.
