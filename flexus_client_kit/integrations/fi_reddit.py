"""
Reddit Integration - thin client that calls Flexus GraphQL API.
All Reddit logic is in backend - this module just forwards requests.
Bots use this to interact with Reddit through Flexus proxy.
"""

import logging
from typing import TYPE_CHECKING, Any

import gql

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("reddit")


# =============================================================================
# Tool Definition
# =============================================================================


REDDIT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="reddit",
    description="Interact with Reddit via Flexus. op='help' for usage, op='status' to check auth.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation: help, status, hot, new, top, search, submit, comment, vote, etc."},
            "args": {"type": "object", "description": "Operation-specific arguments"},
        },
        "required": [],
    },
)


# No setup schema needed - OAuth is via Flexus UI, not bot config
REDDIT_SETUP_SCHEMA: list = []


HELP = """
Reddit Integration (via Flexus Proxy)
=====================================

All Reddit operations go through Flexus backend which handles authentication,
rate limiting, and content moderation.

== IMPORTANT: BOT RESTRICTIONS ==
Per Reddit's Responsible Builder Policy, bots cannot perform actions that
manipulate Reddit's features. The following operations are NOT available to bots:
- Voting (upvote/downvote)
- Saving/unsaving content
These actions can only be performed by users through Flexus UI.

== AUTH ==
reddit(op="status")
    Check if Reddit is authorized and show account info.
    If not authorized, shows link to connect Reddit in Flexus.

reddit(op="me")
    Get your Reddit profile information.

== READ CONTENT ==
reddit(op="hot", args={"subreddit": "python", "limit": 25})
    Get hot posts from a subreddit.

reddit(op="new", args={"subreddit": "python", "limit": 25})
    Get new posts from a subreddit.

reddit(op="top", args={"subreddit": "python", "time": "week", "limit": 25})
    Get top posts. time: hour, day, week, month, year, all

reddit(op="search", args={"query": "machine learning", "subreddit": "python", "limit": 25})
    Search Reddit. subreddit is optional (searches all if omitted).

reddit(op="subreddit_info", args={"subreddit": "python"})
    Get information about a subreddit.

reddit(op="inbox", args={"filter": "unread", "limit": 25})
    Get inbox messages. filter: inbox, unread, sent, messages, mentions

== WRITE CONTENT ==
reddit(op="submit", args={"subreddit": "test", "title": "My Post", "text": "Post body"})
    Submit a text post.

reddit(op="submit", args={"subreddit": "test", "title": "My Link", "url": "https://..."})
    Submit a link post.

reddit(op="comment", args={"parent_id": "t3_abc123", "text": "My comment"})
    Comment on a post or reply to a comment.
    parent_id: t3_xxx for posts, t1_xxx for comments

reddit(op="delete", args={"thing_id": "t3_abc123"})
    Delete your own post or comment.

reddit(op="edit", args={"thing_id": "t3_abc123", "text": "Updated text"})
    Edit your own post or comment.

reddit(op="report", args={"thing_id": "t3_abc123", "reason": "spam"})
    Report a post or comment.

== MESSAGING ==
reddit(op="send_message", args={"to": "username", "subject": "Hi", "text": "Message body"})
    Send a private message.

reddit(op="mark_read", args={"thing_ids": ["t4_abc", "t4_def"]})
    Mark messages as read.

== SUBSCRIPTION ==
reddit(op="subscribe", args={"subreddit": "python"})
    Subscribe to a subreddit.

reddit(op="unsubscribe", args={"subreddit": "python"})
    Unsubscribe from a subreddit.
"""


# Operations blocked for bots per Reddit's Responsible Builder Policy
BOT_BLOCKED_OPERATIONS = {"vote", "save", "unsave"}

BOT_BLOCKED_MESSAGE = """
This operation is not available to bots per Reddit's Responsible Builder Policy.
Bots must not manipulate Reddit's features (voting, karma).
This action can only be performed by users through Flexus UI.
""".strip()


# =============================================================================
# Integration Class
# =============================================================================


class IntegrationReddit:
    """
    Thin wrapper that calls Flexus GraphQL API for Reddit operations.
    All Reddit logic is in backend - this just forwards requests and formats responses.
    """

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: "ckit_bot_exec.RobotContext",
    ):
        self.fclient = fclient
        self.rcx = rcx
        self._ws_id = rcx.persona.ws_id
        self._fuser_id = rcx.persona.owner_fuser_id

    async def _execute_gql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query against Flexus backend."""
        try:
            http = await self.fclient.use_http()
            async with http as h:
                result = await h.execute(gql.gql(query), variable_values=variables or {})
                return result
        except Exception as e:
            logger.error("GraphQL error: %s", str(e), exc_info=True)
            raise

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: dict[str, Any],
    ) -> str:
        """Handle tool calls from LLM."""
        op = model_produced_args.get("op", "help")
        args = model_produced_args.get("args", {})

        try:
            # Check if operation is blocked for bots
            if op in BOT_BLOCKED_OPERATIONS:
                return f"Error: Operation '{op}' is not available.\n\n{BOT_BLOCKED_MESSAGE}"

            if op == "help":
                return HELP

            if op == "status":
                return await self._op_status()

            if op == "me":
                return await self._op_me()

            # Read operations
            if op in ("hot", "new", "top", "rising", "controversial"):
                return await self._op_listing(op, args)

            if op == "search":
                return await self._op_search(args)

            if op == "inbox":
                return await self._op_inbox(args)

            if op == "subreddit_info":
                return await self._op_subreddit_info(args)

            # Write operations
            if op == "submit":
                return await self._op_submit(args)

            if op == "comment":
                return await self._op_comment(args)

            if op == "delete":
                return await self._op_delete(args)

            if op == "edit":
                return await self._op_edit(args)

            if op == "report":
                return await self._op_report(args)

            # Messaging
            if op == "send_message":
                return await self._op_send_message(args)

            if op == "mark_read":
                return await self._op_mark_read(args)

            # Subscription
            if op == "subscribe":
                return await self._op_subscribe(args)

            if op == "unsubscribe":
                return await self._op_unsubscribe(args)

            return f"Unknown operation: {op}\n\nUse reddit(op='help') to see available operations."

        except Exception as e:
            logger.error("reddit op=%s error: %s", op, str(e), exc_info=True)
            return f"Error: {str(e)}"

    # =========================================================================
    # Status & Auth
    # =========================================================================

    async def _op_status(self) -> str:
        """Check Reddit authorization status."""
        result = await self._execute_gql(
            """
            query RedditStatus($ws_id: String!) {
                reddit_status(ws_id: $ws_id) {
                    authorized
                    username
                    link_karma
                    comment_karma
                    error
                }
            }
            """,
            {"ws_id": self._ws_id},
        )

        status = result.get("reddit_status", {})

        r = "Reddit Integration Status\n"
        r += "=" * 40 + "\n"

        if status.get("authorized"):
            r += "Status: AUTHORIZED\n"
            r += f"Username: u/{status.get('username')}\n"
            r += f"Link Karma: {status.get('link_karma', 0)}\n"
            r += f"Comment Karma: {status.get('comment_karma', 0)}\n"
        else:
            r += "Status: NOT AUTHORIZED\n"
            error = status.get("error", "Reddit not connected")
            r += f"Error: {error}\n"
            r += "\nTo connect Reddit:\n"
            r += "1. Go to Flexus Settings > Integrations\n"
            r += "2. Click 'Connect Reddit'\n"
            r += "3. Authorize Flexus to access your Reddit account\n"

        return r

    async def _op_me(self) -> str:
        """Get current user's Reddit profile."""
        result = await self._execute_gql(
            """
            query RedditMe($ws_id: String!) {
                reddit_me(ws_id: $ws_id) {
                    success
                    username
                    link_karma
                    comment_karma
                    created_utc
                    error
                }
            }
            """,
            {"ws_id": self._ws_id},
        )

        me = result.get("reddit_me", {})

        if not me.get("success"):
            return f"Error: {me.get('error', 'Failed to get user info')}"

        r = f"Reddit User: u/{me.get('username')}\n"
        r += f"Link Karma: {me.get('link_karma', 0)}\n"
        r += f"Comment Karma: {me.get('comment_karma', 0)}\n"

        return r

    # =========================================================================
    # Read Operations
    # =========================================================================

    async def _op_listing(self, sort: str, args: dict[str, Any]) -> str:
        """Get posts from a subreddit."""
        subreddit = args.get("subreddit", "all")
        limit = min(args.get("limit", 25), 100)
        time_filter = args.get("time")
        after = args.get("after")

        result = await self._execute_gql(
            """
            query RedditListing($ws_id: String!, $subreddit: String!, $sort: String!, $limit: Int!, $time_filter: String, $after: String) {
                reddit_listing(ws_id: $ws_id, subreddit: $subreddit, sort: $sort, limit: $limit, time_filter: $time_filter, after: $after) {
                    success
                    items {
                        thing_id
                        title
                        author
                        subreddit
                        score
                        num_comments
                        permalink
                        created_utc
                        is_self
                    }
                    after
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "subreddit": subreddit,
                "sort": sort,
                "limit": limit,
                "time_filter": time_filter,
                "after": after,
            },
        )

        listing = result.get("reddit_listing", {})

        if not listing.get("success"):
            return f"Error: {listing.get('error', 'Failed to get listing')}"

        items = listing.get("items", [])
        after_cursor = listing.get("after")

        r = f"r/{subreddit} - {sort} ({len(items)} posts)\n"
        r += "=" * 50 + "\n\n"

        for i, post in enumerate(items, 1):
            r += f"{i}. [{post.get('score', 0)}] {post.get('title', '')[:70]}\n"
            r += f"   by u/{post.get('author', '[deleted]')} | {post.get('num_comments', 0)} comments\n"
            r += f"   ID: {post.get('thing_id')} | {post.get('permalink', '')}\n\n"

        if after_cursor:
            r += f"\nMore posts available. Use after=\"{after_cursor}\" to get next page.\n"

        return r

    async def _op_search(self, args: dict[str, Any]) -> str:
        """Search Reddit."""
        query = args.get("query", "")
        if not query:
            return "Error: query is required for search"

        subreddit = args.get("subreddit")
        sort = args.get("sort", "relevance")
        time_filter = args.get("time", "all")
        limit = min(args.get("limit", 25), 100)

        result = await self._execute_gql(
            """
            query RedditSearch($ws_id: String!, $query: String!, $subreddit: String, $sort: String!, $time_filter: String!, $limit: Int!) {
                reddit_search(ws_id: $ws_id, query: $query, subreddit: $subreddit, sort: $sort, time_filter: $time_filter, limit: $limit) {
                    success
                    items {
                        thing_id
                        title
                        author
                        subreddit
                        score
                        num_comments
                        permalink
                    }
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "query": query,
                "subreddit": subreddit,
                "sort": sort,
                "time_filter": time_filter,
                "limit": limit,
            },
        )

        search = result.get("reddit_search", {})

        if not search.get("success"):
            return f"Error: {search.get('error', 'Search failed')}"

        items = search.get("items", [])
        scope = f"r/{subreddit}" if subreddit else "all of Reddit"

        r = f"Search results for '{query}' in {scope} ({len(items)} results)\n"
        r += "=" * 50 + "\n\n"

        for i, post in enumerate(items, 1):
            r += f"{i}. [{post.get('score', 0)}] {post.get('title', '')[:70]}\n"
            r += f"   r/{post.get('subreddit', '')} by u/{post.get('author', '[deleted]')}\n"
            r += f"   ID: {post.get('thing_id')}\n\n"

        return r

    async def _op_inbox(self, args: dict[str, Any]) -> str:
        """Get inbox messages."""
        filter_type = args.get("filter", "inbox")
        limit = min(args.get("limit", 25), 100)

        result = await self._execute_gql(
            """
            query RedditInbox($ws_id: String!, $filter_type: String!, $limit: Int!) {
                reddit_inbox(ws_id: $ws_id, filter_type: $filter_type, limit: $limit) {
                    success
                    items {
                        thing_id
                        author
                        subject
                        body
                        created_utc
                        was_comment
                        is_new
                    }
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "filter_type": filter_type,
                "limit": limit,
            },
        )

        inbox = result.get("reddit_inbox", {})

        if not inbox.get("success"):
            return f"Error: {inbox.get('error', 'Failed to get inbox')}"

        items = inbox.get("items", [])

        r = f"Inbox - {filter_type} ({len(items)} items)\n"
        r += "=" * 50 + "\n\n"

        for i, msg in enumerate(items, 1):
            new_marker = "[NEW] " if msg.get("is_new") else ""
            msg_type = "comment" if msg.get("was_comment") else "message"
            r += f"{i}. {new_marker}[{msg_type}] from u/{msg.get('author', '[deleted]')}\n"
            if msg.get("subject"):
                r += f"   Subject: {msg.get('subject')}\n"
            body_preview = (msg.get("body", "")[:100] + "...") if len(msg.get("body", "")) > 100 else msg.get("body", "")
            r += f"   {body_preview}\n"
            r += f"   ID: {msg.get('thing_id')}\n\n"

        return r

    async def _op_subreddit_info(self, args: dict[str, Any]) -> str:
        """Get subreddit information."""
        subreddit = args.get("subreddit", "")
        if not subreddit:
            return "Error: subreddit is required"

        result = await self._execute_gql(
            """
            query RedditSubredditInfo($ws_id: String!, $subreddit: String!) {
                reddit_subreddit_info(ws_id: $ws_id, subreddit: $subreddit) {
                    success
                    name
                    display_name
                    title
                    description
                    subscribers
                    public_description
                    over18
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "subreddit": subreddit,
            },
        )

        info = result.get("reddit_subreddit_info", {})

        if not info.get("success"):
            return f"Error: {info.get('error', 'Failed to get subreddit info')}"

        r = f"r/{info.get('display_name', subreddit)}\n"
        r += "=" * 50 + "\n"
        r += f"Title: {info.get('title', '')}\n"
        r += f"Subscribers: {info.get('subscribers', 0):,}\n"
        r += f"NSFW: {'Yes' if info.get('over18') else 'No'}\n"
        if info.get("public_description"):
            r += f"\n{info.get('public_description')}\n"

        return r

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def _op_submit(self, args: dict[str, Any]) -> str:
        """Submit a post."""
        subreddit = args.get("subreddit", "")
        title = args.get("title", "")
        text = args.get("text")
        url = args.get("url")
        flair_id = args.get("flair_id")
        nsfw = args.get("nsfw", False)
        spoiler = args.get("spoiler", False)

        if not subreddit:
            return "Error: subreddit is required"
        if not title:
            return "Error: title is required"
        if not text and not url:
            return "Error: either text or url is required"

        result = await self._execute_gql(
            """
            mutation RedditSubmitPost($ws_id: String!, $subreddit: String!, $title: String!, $text: String, $url: String, $flair_id: String, $nsfw: Boolean!, $spoiler: Boolean!) {
                reddit_submit_post(ws_id: $ws_id, subreddit: $subreddit, title: $title, text: $text, url: $url, flair_id: $flair_id, nsfw: $nsfw, spoiler: $spoiler) {
                    success
                    post_id
                    post_url
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "subreddit": subreddit,
                "title": title,
                "text": text,
                "url": url,
                "flair_id": flair_id,
                "nsfw": nsfw,
                "spoiler": spoiler,
            },
        )

        submit = result.get("reddit_submit_post", {})

        if not submit.get("success"):
            return f"Error: {submit.get('error', 'Failed to submit post')}"

        r = "Post submitted successfully!\n"
        r += f"Post ID: {submit.get('post_id')}\n"
        r += f"URL: {submit.get('post_url')}\n"

        return r

    async def _op_comment(self, args: dict[str, Any]) -> str:
        """Submit a comment."""
        parent_id = args.get("parent_id", "")
        text = args.get("text", "")

        if not parent_id:
            return "Error: parent_id is required (t3_xxx for posts, t1_xxx for comments)"
        if not text:
            return "Error: text is required"

        result = await self._execute_gql(
            """
            mutation RedditComment($ws_id: String!, $parent_id: String!, $text: String!) {
                reddit_comment(ws_id: $ws_id, parent_id: $parent_id, text: $text) {
                    success
                    comment_id
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "parent_id": parent_id,
                "text": text,
            },
        )

        comment = result.get("reddit_comment", {})

        if not comment.get("success"):
            return f"Error: {comment.get('error', 'Failed to post comment')}"

        return f"Comment posted! ID: {comment.get('comment_id')}"

    async def _op_vote(self, args: dict[str, Any]) -> str:
        """Vote on a post or comment."""
        thing_id = args.get("thing_id", "")
        direction = args.get("direction", 0)

        if not thing_id:
            return "Error: thing_id is required"

        result = await self._execute_gql(
            """
            mutation RedditVote($ws_id: String!, $thing_id: String!, $direction: Int!) {
                reddit_vote(ws_id: $ws_id, thing_id: $thing_id, direction: $direction) {
                    success
                    error
                }
            }
            """,
            {
                "ws_id": self._ws_id,
                "thing_id": thing_id,
                "direction": direction,
            },
        )

        vote = result.get("reddit_vote", {})

        if not vote.get("success"):
            return f"Error: {vote.get('error', 'Vote failed')}"

        action = {1: "Upvoted", -1: "Downvoted", 0: "Vote removed"}
        return f"{action.get(direction, 'Voted on')} {thing_id}"

    async def _op_save(self, args: dict[str, Any]) -> str:
        """Save a post or comment."""
        thing_id = args.get("thing_id", "")
        if not thing_id:
            return "Error: thing_id is required"

        result = await self._execute_gql(
            """
            mutation RedditSave($ws_id: String!, $thing_id: String!) {
                reddit_save(ws_id: $ws_id, thing_id: $thing_id) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_id": thing_id},
        )

        save = result.get("reddit_save", {})
        if not save.get("success"):
            return f"Error: {save.get('error', 'Save failed')}"

        return f"Saved {thing_id}"

    async def _op_unsave(self, args: dict[str, Any]) -> str:
        """Unsave a post or comment."""
        thing_id = args.get("thing_id", "")
        if not thing_id:
            return "Error: thing_id is required"

        result = await self._execute_gql(
            """
            mutation RedditUnsave($ws_id: String!, $thing_id: String!) {
                reddit_unsave(ws_id: $ws_id, thing_id: $thing_id) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_id": thing_id},
        )

        unsave = result.get("reddit_unsave", {})
        if not unsave.get("success"):
            return f"Error: {unsave.get('error', 'Unsave failed')}"

        return f"Unsaved {thing_id}"

    async def _op_delete(self, args: dict[str, Any]) -> str:
        """Delete a post or comment."""
        thing_id = args.get("thing_id", "")
        if not thing_id:
            return "Error: thing_id is required"

        result = await self._execute_gql(
            """
            mutation RedditDelete($ws_id: String!, $thing_id: String!) {
                reddit_delete(ws_id: $ws_id, thing_id: $thing_id) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_id": thing_id},
        )

        delete = result.get("reddit_delete", {})
        if not delete.get("success"):
            return f"Error: {delete.get('error', 'Delete failed')}"

        return f"Deleted {thing_id}"

    async def _op_edit(self, args: dict[str, Any]) -> str:
        """Edit a post or comment."""
        thing_id = args.get("thing_id", "")
        text = args.get("text", "")

        if not thing_id:
            return "Error: thing_id is required"
        if not text:
            return "Error: text is required"

        result = await self._execute_gql(
            """
            mutation RedditEdit($ws_id: String!, $thing_id: String!, $text: String!) {
                reddit_edit(ws_id: $ws_id, thing_id: $thing_id, text: $text) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_id": thing_id, "text": text},
        )

        edit = result.get("reddit_edit", {})
        if not edit.get("success"):
            return f"Error: {edit.get('error', 'Edit failed')}"

        return f"Edited {thing_id}"

    async def _op_report(self, args: dict[str, Any]) -> str:
        """Report a post or comment."""
        thing_id = args.get("thing_id", "")
        reason = args.get("reason", "")

        if not thing_id:
            return "Error: thing_id is required"
        if not reason:
            return "Error: reason is required"

        result = await self._execute_gql(
            """
            mutation RedditReport($ws_id: String!, $thing_id: String!, $reason: String!) {
                reddit_report(ws_id: $ws_id, thing_id: $thing_id, reason: $reason) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_id": thing_id, "reason": reason},
        )

        report = result.get("reddit_report", {})
        if not report.get("success"):
            return f"Error: {report.get('error', 'Report failed')}"

        return f"Reported {thing_id}"

    # =========================================================================
    # Messaging
    # =========================================================================

    async def _op_send_message(self, args: dict[str, Any]) -> str:
        """Send a private message."""
        to = args.get("to", "")
        subject = args.get("subject", "")
        text = args.get("text", "")

        if not to:
            return "Error: to (username) is required"
        if not subject:
            return "Error: subject is required"
        if not text:
            return "Error: text is required"

        result = await self._execute_gql(
            """
            mutation RedditSendMessage($ws_id: String!, $to: String!, $subject: String!, $text: String!) {
                reddit_send_message(ws_id: $ws_id, to: $to, subject: $subject, text: $text) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "to": to, "subject": subject, "text": text},
        )

        send = result.get("reddit_send_message", {})
        if not send.get("success"):
            return f"Error: {send.get('error', 'Failed to send message')}"

        return f"Message sent to u/{to}"

    async def _op_mark_read(self, args: dict[str, Any]) -> str:
        """Mark messages as read."""
        thing_ids = args.get("thing_ids", [])
        if not thing_ids:
            return "Error: thing_ids is required (list of message IDs)"

        result = await self._execute_gql(
            """
            mutation RedditMarkRead($ws_id: String!, $thing_ids: [String!]!) {
                reddit_mark_read(ws_id: $ws_id, thing_ids: $thing_ids) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "thing_ids": thing_ids},
        )

        mark = result.get("reddit_mark_read", {})
        if not mark.get("success"):
            return f"Error: {mark.get('error', 'Failed to mark as read')}"

        return f"Marked {len(thing_ids)} message(s) as read"

    # =========================================================================
    # Subscription
    # =========================================================================

    async def _op_subscribe(self, args: dict[str, Any]) -> str:
        """Subscribe to a subreddit."""
        subreddit = args.get("subreddit", "")
        if not subreddit:
            return "Error: subreddit is required"

        result = await self._execute_gql(
            """
            mutation RedditSubscribe($ws_id: String!, $subreddit: String!) {
                reddit_subscribe(ws_id: $ws_id, subreddit: $subreddit) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "subreddit": subreddit},
        )

        sub = result.get("reddit_subscribe", {})
        if not sub.get("success"):
            return f"Error: {sub.get('error', 'Subscribe failed')}"

        return f"Subscribed to r/{subreddit}"

    async def _op_unsubscribe(self, args: dict[str, Any]) -> str:
        """Unsubscribe from a subreddit."""
        subreddit = args.get("subreddit", "")
        if not subreddit:
            return "Error: subreddit is required"

        result = await self._execute_gql(
            """
            mutation RedditUnsubscribe($ws_id: String!, $subreddit: String!) {
                reddit_unsubscribe(ws_id: $ws_id, subreddit: $subreddit) {
                    success
                    error
                }
            }
            """,
            {"ws_id": self._ws_id, "subreddit": subreddit},
        )

        unsub = result.get("reddit_unsubscribe", {})
        if not unsub.get("success"):
            return f"Error: {unsub.get('error', 'Unsubscribe failed')}"

        return f"Unsubscribed from r/{subreddit}"
