PREAMBLE = """In 1957, the University of Waterloo opened its doors to 74 engineering students with co-operative education as its cornerstone.
Today, with more than 42,000+ students attending annually, Waterloo is #1 in Canada for experiential learning and employer-student connections. 
With a global network spanning more than 244,000 alumni in 156 countries, Waterloo attracts world-class scholars including a Nobel Laureate, leads in providing work-integrated learning opportunities with 8,000+ active co-op employers and fosters an entrepreneurial spirit that’s created 5,000+ jobs through Velocity alone, Canada’s most productive startup incubator by private investment.
The University of Waterloo continues to spur innovation to solve problems on a global scale. Together, with the help of our partners and community, we can accomplish even more.
The University of Waterloo is home to 6 Faculties: Arts, Engineering, Environment, Health, Mathematics, and Science. Each faculty offers a wide range of programs and opportunities for students to explore their interests and passions under the leadership of talented faculty and the Waterloo administration. 

The above is a preamble about the University of Waterloo. You will be given a reddit post or comment from the University of Waterloo subreddit and you will create a unique and diverse persona based the content in the post. A persona is a couple sentences maximum about the person with a creative backstory that adheres to the content in the post."""

AUTHOR_POST_PROMPT = """{PREAMBLE}
## Post
{post}
Based on the above post, who do you think would have been most likely to write this post?"""

AUTHOR_COMMENT_PROMPT = """{PREAMBLE}

## Post
{post}

## Comment
{comment}
Based on the above comment, who do you think would have been most likely to write this comment?"""

##NOTE: update prompts to be like this or like how we did for maya
AUTHOR_COMMENT_NO_POST_PROMPT = """## Comment
{comment}
Based on the above reddit comment, who do you think would have been most likely to write this comment?"""

RESPOND_TO_COMMENT_NO_POST_PROMPT = """## Comment
{comment}
Based on the above reddit comment, who would be most likely to respond to this comment?"""