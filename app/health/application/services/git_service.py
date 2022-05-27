import logging

from git import Repo, GitError

from app.health.application.services.exceptions.get_current_commit_hash_exception import GetCurrentCommitHashException


class GitService:
    __PATH_TO_REPO = "/home/hdhsuser"

    def get_current_commit_hash(self) -> str:
        """
        Retrieves current HDHS repository commit hash.

        :raises GetCurrentCommitHashException
        """
        logger = logging.getLogger()
        try:
            logger.info("Obtaining current git commit hash...")
            repo = Repo(self.__PATH_TO_REPO)
            commit_hash = repo.git.rev_parse("HEAD")
            logger.info("Current git commit hash: " + commit_hash)
            return commit_hash
        except GitError as ge:
            logger.error(str(ge))
            raise GetCurrentCommitHashException(str(ge))
