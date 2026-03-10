from django.db import models


class OMRResult(models.Model):
    name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.score}"


class DebugResult(models.Model):
    name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.score}"


class DSAResult(models.Model):
    name = models.CharField(max_length=200)
    q1_score = models.FloatField(default=0)
    q2_score = models.FloatField(default=0)
    q3_score = models.FloatField(default=0)
    total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.total}"


class FinalResult(models.Model):
    name = models.CharField(max_length=200)
    omr_score = models.FloatField(default=0)
    debug_score = models.FloatField(default=0)
    dsa_score = models.FloatField(default=0)
    puzzle_score = models.FloatField(default=0)
    total = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.rank} {self.name} — {self.total}"
