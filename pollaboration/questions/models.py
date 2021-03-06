from django.db import models
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify
from django.db.models import Q, Count
from accounts.models import MyUser
from django.conf import settings
from datetime import date
from django.core.urlresolvers import reverse

class Question(models.Model):
    question = models.CharField(max_length=250)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, null=True, blank=True, related_name='submissions')
    answered_by = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True, default=None, related_name='questions_answered')
    slug = models.SlugField(max_length=250, blank=True)
    created = models.DateField(auto_now_add=True, default=date.today())
    modified = models.DateField(auto_now=True, default=date.today())

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __unicode__(self):
        return u'%s' %(self.question)

    def get_absolute_url(self):
        return reverse('questions.views.current_question', args=[str(self.id)])

    def _get_anonymous_vote_count(self):
        return q.answer_set.filter(votes__voter=None).count()
    anonymous_vote_count=property(_get_anonymous_vote_count)

    def _get_total_vote_count(self):
        return self.answer_set.all().aggregate(Count('votes')).values()[0]
    total_vote_count=property(_get_total_vote_count)

    def _get_registered_vote_count(self):
        return self.answered_by.count()
    registered_vote_count=property(_get_registered_vote_count)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.question)
        super(Question, self).save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers')
    answer = models.CharField(max_length=250)
    selected_by = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True, default=None, related_name='answer_selections')
    modified = models.DateField(auto_now=True, default=date.today())

    class Meta:
        verbose_name = _('answer')
        verbose_name_plural = _('answers')

    def _get_anonymous_vote_count(self):
        return self.votes.filter(voter=None).count()
    anonymous_vote_count=property(_get_anonymous_vote_count)

    def _get_registered_vote_count(self):
        return self.votes.filter(~Q(voter=None)).count()
    registered_vote_count=property(_get_registered_vote_count)

    def __unicode__(self):
        return u'%s' %(self.answer)


class Vote(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=None, related_name='votes')
    answer = models.ForeignKey(Answer, related_name='votes')
    created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('vote')
        verbose_name_plural = _('votes')
