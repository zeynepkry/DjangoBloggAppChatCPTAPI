from django.utils import timezone
from celery import shared_task
import csv
import pandas as pd
from blog.models import Post, Category, CSVProgress
from blog.utils import get_chatgpt_response, get_chatgpt_summary

@shared_task
def generate_blog_posts_from_reddit_excel():
    file_path = 'blogapp/data/reddit.xlsx'
    
    # Get or create progress tracking entry for reddit Excel file
    progress, _ = CSVProgress.objects.get_or_create(id=2)

    # Check if all rows are processed
    if progress.all_processed:
        print("All rows in reddit.xlsx already processed. Task will not continue.")
        return

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file_path)

        # Filter rows where 'subreddit' is 'datascience'
        filtered_df = df[df['subreddit'].str.strip().str.lower() == 'datascience']
        print("Filtered data where subreddit is 'datascience' loaded.")

        # Convert filtered DataFrame to a list of dictionaries to work with indexing
        filtered_rows = filtered_df.to_dict('records')

        # Ensure there are rows left to process
        if progress.last_row < len(filtered_rows):
            row = filtered_rows[progress.last_row]
            
            # Debug: Print the current row's details
            print(f"Processing row {progress.last_row} with title: {row.get('title', 'Default Title')}")

            # Extract data from the row
            title = row.get("title", "Default Title")
            body_summary = row.get("body_summary", "Default Summary")
      
            prompt = f"""
            Write a detailed and well-organized educational blog article based on the following summary: {body_summary}. 
            The article should be up to 1,500 words in length, easy to follow, and structured for optimal readability. 
            Include the following elements:

            Introduction:

                Start with a compelling introduction that grabs the reader’s attention and introduces the importance of the topic.
                Include an engaging hook that makes the reader want to continue reading.
                Briefly summarize what the reader will learn in the article.
                Main Sections:

                Break the content into 3-5 main sections that cover key points or subtopics related to the main theme.
                Each section should begin with a clear heading, and provide an explanation or discussion about the subtopic.
                Include real-life examples, data, or case studies where applicable to illustrate the points.
                Where relevant, include a step-by-step guide or process if it helps to explain the topic better.
                Tips and Practical Advice:

                Add a section that provides readers with practical tips, actionable advice, or solutions that they can implement based on the topic.
                These tips should be easy to follow and relevant to the main topic.
                Visual Aids and Formatting:

                Mention any appropriate use of images, charts, or infographics that could help clarify complex ideas (though they will not be included in the generated text).
                Suggest where bullet points, numbered lists, or tables could be added to improve readability.
                Conclusion:

                Conclude the article by summarizing the main points discussed.
                Reinforce why the topic is significant, and offer final thoughts or a call to action that encourages the reader to apply what they've learned or explore further.
                References and Further Reading:

                Include a section recommending further reading materials, useful links, or resources to explore if the reader wants to learn more.
                Optionally, cite credible sources for any claims or statistics mentioned in the article.
                Tone and Style:

                The tone should be informative and educational but approachable and easy to understand, suitable for readers who may be new to the topic.
                Avoid jargon, unless necessary, and explain any complex terms.
                The style should be conversational yet professional, encouraging readers to stay engaged.
                This structure ensures the article will be informative, engaging, and well-organized, with a logical flow from introduction to conclusion.
                Do not include the title in the article, skip to a new parahraph after each part of the article, introduction, bullet points etc. Make sure you have double space between paragraphs.
                Structure the article to ensure readability with well-formed paragraphs and double spacing between paragraphs. Do not include the title within the body of the article, and avoid using numbered lists or bullet points for section headers.Use HTML paragraph tags <p> to separate each paragraph, ensuring there is a visible gap between them.Ensure the article reads like a fluid, human-written piece, focusing on a natural and engaging style.
            """

            # Generate summary from ChatGPT API (pseudo-code, replace with your actual API call)
            generated_content = get_chatgpt_response(prompt)
            generated_summary = get_chatgpt_summary(generated_content)

            # Save post directly using generated summary
            category, _ = Category.objects.get_or_create(name="Reddit Import")
            Post.objects.create(
                title=title,
                content=generated_content,  # Use generated summary as the content
                summary=generated_summary,  # Summary is the same as content here
                created_at=timezone.now(),
                category=category,
                is_published=True
            )

            # Update progress to next row and save
            progress.last_row += 1
            progress.save()

        else:
            # Mark as processed if no more rows
            progress.all_processed = True
            progress.save()
            print("All rows in reddit.xlsx processed.")
    except Exception as e:
        print(f"Error creating blog post from reddit.xlsx: {e}")