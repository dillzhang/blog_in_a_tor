# Blog_in_a_tor

## Collaborators
|   **Member**   |       **Role**      |
|:--------------:|:-------------------:|
|Chun Hung Li    | User Experience     |
|Dennis Yatunin  | Backend             |
|Dillon Zhang    | Middleware          |
|Samuel Zhang    | Leader              |

## Timetable

**DUE 10/19**

- [ ] Outline basic site
- [ ] Outline database structure
- [ ] Implement Login Server

## Backend Functions
### User Account Functions
- [ ] check_login_info(username, password)
Returns whether or not the database has a user with the given username and password
- [ ] register_new_user(username, password, confirm_password, email)
Enters a new user with the given information into the database and returns None (or possible error messages)
- [ ] modify_password(username, password, new_password, confirm_password):
Changes the user's hashed password in the database and returns None (or possible error messages)
- [ ] modify_email(username, password, new_email)
Changes the user's email in the database and returns None (or possible error messages)
### Post Functions
- [ ] new_post(username, post, heading=None)
Enters the new post into the database and returns the id that was generated for it (or an error message if there is no account with the given username); if no heading is provided, one is automatically generated that consists of the first 10 characters plus '...'
- [ ] get_post(post_id)
Returns a list consisting of the post, its heading, and its timestamp, or None if there is no post in the database with the given id
- [ ] get_user_posts(username)
Returns a list of lists consisting of the user's posts, their headings, their timestamps, and their ids, or an empty list if the user has no posts or doesn't exist
- [ ] get_recent_posts()
Returns a list of lists consisting of the 10 most recent posts, their headings, their timestamps, and their ids, or an empty list if there are no posts in the database
- [ ] modify_post(post_id, new_post)
Changes the post with the given id to the new post provided, updates the post's timestamp, and returns None
- [ ] remove_post(post_id)
Removes the post with the given id from the database and returns None
### Comment Functions
- [ ] new_comment(username, comment, heading=None)
Enters the new comment into the database and returns the id that was generated for it (or an error message if there is no account with the given username); if no heading is provided, one is automatically generated that consists of the first 10 characters plus '...'
- [ ] get_comment(comment_id)
Returns a list consisting of the comment, its heading, and its timestamp, or None if there is no comment in the database with the given id
- [ ] get_user_comments(username)
Returns a list of lists consisting of the user's comments, their headings, their timestamps, and their ids, or an empty list if the user has no comments or doesn't exist
- [ ] get_recent_comments()
Returns a list of lists consisting of the 10 most recent comments, their headings, their timestamps, and their ids, or an empty list if there are no comments in the database
- [ ] modify_comment(comment_id, new_comment)
Changes the comment with the given id to the new comment provided, updates the comment's timestamp, and returns None
- [ ] remove_comment(comment_id)
Removes the comment with the given id from the database and returns None
