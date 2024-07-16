from enum import Enum, IntFlag


class UserAccountState(IntFlag):
    Operational = 0
    Suspended = 1


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'


class BotType(str, Enum):
    DEDICATED_BOT = 'dedicated',
    LEADGURU_BOT = 'leadguru'


class GoogleCloudFolder(str, Enum):
    SLACK_PROFILE_FILES = "Slack_profile"
    TICKET_FILES = "Ticket"


class SourceType(str, Enum):
    SLACK = 'slack'
    DISCORD = 'discord'


class UserAction(str, Enum):
    PAUSE_SOURCE = 'monitoring.pause.source'
    UNPAUSE_SOURCE = 'monitoring.unpause.source'
    STOP_CHANNEL = 'monitoring.stop.channel'
    STOP_SOURCE = 'monitoring.stop.source'
    START_CHANNEL = 'monitoring.start.channel'
    START_SOURCE = 'monitoring.start.source'
    LOGIN = 'login'
    LEAD_SAVE = 'lead.save'
    CHAT_MESSAGE = 'chat.message'
    ADMIN_CREDITS_ADDED = "admin-creds-added"
    ADMIN_CREDITS_SET = "admin-creds-set"
    INITIAL_CREDITS_SET = "initial-creds-set"


class StatusConnection(str, Enum):
    SOURCES_IN_PROGRESS = 'Sources in progress',
    IN_PROGRESS = 'In progress',
    COMPLETE = 'Complete',
    FAILED = 'Failed'


class DefaultBoards(str, Enum):
    Inbox = 'Inbox',
    Primary = 'Primary board'


class BotEventType(str, Enum):
    CREATE = 'BotAdded'
    UPDATE = 'BotUpdated'
    DELETE = 'BotDeleted'


class ImageName(str, Enum):
    ARROW = 'arrow.png'
    CRY = 'cry.png'
    FIREWORK = 'firework.png'
    HANDS = 'hands.png'
    LOCK = 'lock.png'
    LOGO = 'logo.png'
    MAIL = 'mail.png'
    SAD = 'sad.png'


class FeaturesEnum(str, Enum):
    FEED = 'feed'
    PIPELINES = 'pipelines'
    LEADS = 'leads'
    CONTACTS = 'contacts'
    DASHBOARD = 'dashboard'
    EXPORT = 'export'
    CRM = 'crm'
    MESSAGE_REQUEST = 'message_request'
    DIRECT_MESSAGES = 'dm'
    PEOPLE = 'people'
    TEMPLATES = 'templates'
    BILLING = 'billing'
    PIPEDRIVE = 'pipedrive'
    MASS_DIRECT_MESSAGES = 'mass_direct_messages'
    TARGETS = 'targets'
    MY_TEAM = 'my_team'
    SCHEDULED_MESSAGES = 'scheduled_messages'
    SOURCES = 'sources'
    ALGORITHMS = 'algorithms'


class FeatureOptions(str, Enum):
    BASIC = 'basic'
    ADVANCED = 'advanced'
