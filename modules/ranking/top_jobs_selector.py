class TopJobsSelector:
    """
    Selects the highest-ranked jobs.

    This class exists to keep the ranking stage independent
    from the AI analysis stage.
    """

    def __init__(self, top_n=3):
        self.top_n = top_n

    def select(self, ranked_jobs):
        """
        Returns the highest-ranked jobs.

        Parameters
        ----------
        ranked_jobs : list
            Output from JobRanker.rank()

        Returns
        -------
        list
            Top N ranked jobs.
        """

        return ranked_jobs[: self.top_n]