import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from bs4 import BeautifulSoup

class SimpleEmailExtractor:
    def __init__(self):
        load_dotenv()
        self.graph_client = self.setup_graph_client()
        
    def setup_graph_client(self):
        """Setup Microsoft Graph client"""
        credential = ClientSecretCredential(
            tenant_id=os.getenv('TENANT_ID'),
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET')
        )
        scopes = ['https://graph.microsoft.com/.default']
        return GraphServiceClient(credentials=credential, scopes=scopes)
    
    async def fetch_emails_simple(self, days_back=30, max_emails=1000):
        """Fetch emails with simple query parameters"""
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
            shared_mailbox_email = os.getenv('SHARED_MAILBOX_EMAIL')
            print(f"Fetching emails from {shared_mailbox_email} since {start_date}")

            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                    filter=f"receivedDateTime ge {start_date}",
                    select=["id", "subject", "body", "from", "toRecipients", "ccRecipients", "receivedDateTime", "conversationId", "importance", "hasAttachments"],
                    orderby=["receivedDateTime desc"],
                    top=max_emails
                )
            )
            
            messages = await self.graph_client.users.by_user_id(shared_mailbox_email).messages.get(
                request_configuration=request_config
            )
            return messages.value if messages else []

        except ODataError as e:
            print(f"Graph API Error: {e.error.code} - {e.error.message}")
            return []
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def clean_html_content(self, html_content):
        """Clean HTML content to plain text"""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)

    def email_to_json(self, email):
        """Convert email object to JSON-serializable dictionary"""
        try:
            body_content = ""
            if email.body:
                if email.body.content_type.value == "html":
                    body_content = self.clean_html_content(email.body.content)
                else:
                    body_content = email.body.content or ""

            from_info = {}
            if email.from_ and email.from_.email_address:
                from_info = {
                    "name": email.from_.email_address.name,
                    "address": email.from_.email_address.address
                }

            to_info = []
            if email.to_recipients:
                for recipient in email.to_recipients:
                    if recipient.email_address:
                        to_info.append({
                            "name": recipient.email_address.name,
                            "address": recipient.email_address.address
                        })

            cc_info = []
            if email.cc_recipients:
                for recipient in email.cc_recipients:
                    if recipient.email_address:
                        cc_info.append({
                            "name": recipient.email_address.name,
                            "address": recipient.email_address.address
                        })

            return {
                "id": email.id,
                "conversation_id": email.conversation_id,
                "subject": email.subject or "[No Subject]",
                "body_content": body_content,
                "from": from_info,
                "to": to_info,
                "cc": cc_info,
                "received_datetime": email.received_date_time.isoformat() if email.received_date_time else None,
                "importance": email.importance.value if email.importance else "normal",
                "has_attachments": email.has_attachments if email.has_attachments else False,
                "extracted_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error converting email to JSON: {e}")
            return None

    async def extract_emails_grouped_by_subject(self, days_back=30, output_file="emails_grouped.json"):
        """Extract and group emails by subject"""
        print(f"Starting grouped email extraction for last {days_back} days...")

        emails = await self.fetch_emails_simple(days_back)

        if not emails:
            print("No emails found or error occurred")
            return {}

        print(f"Found {len(emails)} emails. Grouping by subject...")

        grouped_emails = {}
        for email in emails:
            email_json = self.email_to_json(email)
            if not email_json:
                continue

            subject = email_json["subject"].strip() or "[No Subject]"
            entry = {
                "received_datetime": email_json["received_datetime"],
                "body": email_json["body_content"]
            }

            if subject not in grouped_emails:
                grouped_emails[subject] = []
            grouped_emails[subject].append(entry)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(grouped_emails, f, indent=2, ensure_ascii=False)

        print(f"Successfully grouped and saved emails to {output_file}")

        # Sample output
        sample_subject = next(iter(grouped_emails))
        print(f"\nSample Subject Group: {sample_subject}")
        print(f"Total emails under this subject: {len(grouped_emails[sample_subject])}")
        print(f"First email preview: {grouped_emails[sample_subject][0]['body'][:200]}...")

        return grouped_emails

async def main():
    extractor = SimpleEmailExtractor()
    days = int(input("Days back to fetch (default 30): ") or 30)
    filename = input("Output filename (default emails_grouped.json): ") or "emails_grouped.json"
    await extractor.extract_emails_grouped_by_subject(days_back=days, output_file=filename)

if __name__ == "__main__":
    asyncio.run(main())
