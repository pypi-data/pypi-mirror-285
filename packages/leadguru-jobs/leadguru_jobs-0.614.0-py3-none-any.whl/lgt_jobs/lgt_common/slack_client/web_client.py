from google.cloud import storage
from datetime import datetime, timedelta
from lgt_jobs.lgt_data.model import ChatMessage, LeadGuruFile, DedicatedBotModel
from lgt_jobs.lgt_common.slack_client.slack_client import SlackClient
from lgt_jobs.lgt_data.mongo_repository import to_object_id


class SlackMessageConvertService:
    @staticmethod
    def from_slack_response(bot: DedicatedBotModel, message_data: dict, sender_id: str) -> ChatMessage:
        result = ChatMessage()
        result.sender_id = sender_id
        result.bot_id = to_object_id(bot.id)
        result.text = message_data.get('text', '')
        result.user = message_data.get('user', '')
        result.id = message_data.get('ts', '')
        result.attachments = message_data.get('attachments', [])
        result.files = []
        result.user_id = to_object_id(bot.user_id)
        result.source_id = bot.source.source_id
        if 'files' in message_data:
            for file in message_data.get('files'):
                if file.get('mode') != "tombstone" and file.get('url_private_download'):
                    leadguru_file = LeadGuruFile()
                    leadguru_file.id = file['id']
                    leadguru_file.content_type = file['mimetype']
                    leadguru_file.file_name = file['name']
                    leadguru_file.blob_path = f'slack_files/{bot.user_name}/slack_files/{file["id"]}'
                    result.files.append(leadguru_file)

        js_ticks = int(result.id.split('.')[0] + result.id.split('.')[1][3:])
        result.created_at = datetime.fromtimestamp(js_ticks / 1000.0)
        return result


class SlackFilesClient:
    bucket_name = 'lgt_service_file'

    def get_file_url(self, blob_path):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)
        blob = bucket.get_blob(blob_path)
        if not blob:
            return None
        # valid for 3 days
        return blob.generate_signed_url(timedelta(3))


class SlackWebClient:
    def __init__(self, token, cookies=None):
        if isinstance(cookies, list):
            cookies = {c['name']: c['value'] for c in cookies}

        self.client = SlackClient(token, cookies)

    def user_list(self):
        return self.client.users_list()

    def delete_message(self, channel: str, id: str):
        return self.client.delete_message(channel, id)

    def update_message(self, channel: str, id: str, text: str, file_ids=''):
        return self.client.update_message(channel, id, text, file_ids)

    def get_profile(self, user_id):
        return self.client.user_info(user_id)

    def get_im_list(self):
        return self.client.get_im_list()

    def chat_history(self, channel):
        return self.client.conversations_history(channel)

    def post_message(self, to, text):
        return self.client.post_message(to, text)

    def channels_list(self):
        return self.client.get_conversations_list()

    def im_open(self, sender_id):
        return self.client.im_open(sender_id)

    def update_profile(self, profile):
        return self.client.update_profile(profile)

    def get_reactions(self, channel, id):
        return self.client.get_reactions(channel, id)

    def upload_file(self, file, file_name):
        return self.client.upload_file(file, file_name)

    def download_file(self, file_url):
        return self.client.download_file(file_url)

    def delete_file(self, file_id):
        return self.client.delete_file(file_id)

    def share_files(self, files_ids: list, channel: str, text: str = None) -> dict:
        return self.client.share_files(files_ids, channel, text)

    def check_email(self, email: str, user_agent: str) -> bool:
        return self.client.check_email(email, user_agent)

    def confirm_email(self, email: str, user_agent: str, locale: str = 'en-US') -> bool:
        return self.client.confirm_email(email, user_agent, locale)

    def confirm_code(self, email: str, code: str, user_agent: str):
        return self.client.confirm_code(email, code, user_agent)

    def find_workspaces(self, user_agent: str):
        return self.client.find_workspaces(user_agent)

    def conversation_replies(self, channel: str, id: str) -> dict:
        return self.client.conversations_replies(channel, id)

    def create_shared_invite(self):
        return self.client.create_shared_invite()

    def send_slack_invite_to_workspace(self, email: str):
        return self.client.send_slack_invite_to_workspace(email=email)

    def test_auth(self):
        return self.client.test_auth()

    def get_team_info(self):
        return self.client.get_team_info()

    def get_file_info(self, file_id: str):
        return self.client.get_file_info(file_id)

    def channel_join(self, channels):
        return self.client.join_channels(channels)

    def channel_leave(self, channels):
        return self.client.leave_channels(channels)
