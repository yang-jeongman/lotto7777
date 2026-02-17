from django.db import models


class DrawResult(models.Model):
    """로또 추첨 결과"""
    draw_no = models.PositiveIntegerField(unique=True, db_index=True, verbose_name='회차')
    draw_date = models.DateField(verbose_name='추첨일')
    number_1 = models.PositiveSmallIntegerField()
    number_2 = models.PositiveSmallIntegerField()
    number_3 = models.PositiveSmallIntegerField()
    number_4 = models.PositiveSmallIntegerField()
    number_5 = models.PositiveSmallIntegerField()
    number_6 = models.PositiveSmallIntegerField()
    bonus_number = models.PositiveSmallIntegerField(verbose_name='보너스')
    first_prize_amount = models.BigIntegerField(default=0, verbose_name='1등 당첨금')
    first_prize_winners = models.PositiveIntegerField(default=0, verbose_name='1등 당첨자수')
    total_sales = models.BigIntegerField(default=0, verbose_name='총 판매금액')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-draw_no']
        get_latest_by = 'draw_no'
        verbose_name = '추첨 결과'
        verbose_name_plural = '추첨 결과'

    def __str__(self):
        return f'제{self.draw_no}회 ({self.draw_date})'

    @property
    def numbers(self):
        return sorted([
            self.number_1, self.number_2, self.number_3,
            self.number_4, self.number_5, self.number_6,
        ])
