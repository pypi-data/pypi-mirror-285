from abc import ABC
from lgt_jobs.lgt_common.enums.slack_errors import SlackErrors
from lgt_jobs.lgt_common.slack_client.slack_client import SlackClient
from lgt_jobs.lgt_data.model import Source, SlackMemberInformation
from lgt_jobs.lgt_data.mongo_repository import DedicatedBotRepository, SlackContactUserRepository
import logging as log
from pydantic import BaseModel
from lgt_jobs.basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Load Slack people by required bot
"""


class LoadSlackPeopleJobData(BaseBackgroundJobData, BaseModel):
    bot_id: str


class LoadSlackPeopleJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return LoadSlackPeopleJobData

    def exec(self, data: LoadSlackPeopleJobData):
        dedicated_bots_repo = DedicatedBotRepository()
        bot = dedicated_bots_repo.get_one(id=data.bot_id)
        log.info(f'Start Scraping for [{str(bot.user_id)}:{bot.source.source_id}]')

        client = SlackClient(bot.token, bot.cookies)
        try:
            list_users_response = client.users_list()
        except:
            log.error(f'Error to get users [{str(bot.user_id)}:{bot.source.source_id}]')
            return

        members_count = 0
        while True:
            if not list_users_response["ok"] and list_users_response['error'] == SlackErrors.INVALID_AUTH:
                bot.invalid_creds = True
                dedicated_bots_repo.add_or_update(bot)
                log.error(f'Error during listing [{bot.source.source_name}:{bot.source.source_id}] '
                          f'members: {list_users_response["error"]}')
                return

            if not list_users_response.get('members', []):
                log.warning(f'No members in [{str(bot.user_id)}:{bot.source.source_id}]: {list_users_response}')
                return

            for member in list_users_response["members"]:
                if not member.get("profile"):
                    continue

                if member.get("deleted", True) or member.get("id") == 'USLACKBOT':
                    continue

                source = Source()
                source.source_id = bot.source.source_id
                source.source_name = bot.source.source_name
                source.source_type = bot.source.source_type
                member_info: SlackMemberInformation = SlackMemberInformation.from_slack_response(member, source)
                members_count += 1
                member_info_dic = member_info.to_dic()
                member_info_dic.pop('created_at')
                SlackContactUserRepository().collection().update_one({"sender_id": member_info.sender_id,
                                                                      "source.source_id": source.source_id},
                                                                     {"$set": member_info_dic}, upsert=True)

            next_cursor = list_users_response["response_metadata"].get("next_cursor", "")
            if next_cursor == "":
                log.info(f'[{str(bot.user_id)}:{bot.source.source_id}] loading done. {members_count} loaded')
                break

            list_users_response = client.users_list(next_cursor)
