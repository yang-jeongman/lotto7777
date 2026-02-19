"""
동행복권 웹페이지 스크래핑으로 최신 로또 당첨 데이터를 가져오는 커맨드
Usage: python manage.py fetch_latest [--from N] [--to N]
"""
import re
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from apps.analysis.models import DrawResult

RESULT_URL = 'https://www.dhlottery.co.kr/gameResult.do'


class Command(BaseCommand):
    help = '동행복권에서 최신 로또 당첨 데이터를 가져옵니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from', type=int, dest='from_no',
            help='시작 회차 (미지정 시 DB 최신 회차+1부터)',
        )
        parser.add_argument(
            '--to', type=int, dest='to_no',
            help='종료 회차 (미지정 시 최신까지 자동)',
        )

    def handle(self, *args, **options):
        from_no = options.get('from_no')
        to_no = options.get('to_no')

        # DB에서 최신 회차 확인
        if from_no is None:
            latest = DrawResult.objects.order_by('-draw_no').first()
            from_no = (latest.draw_no + 1) if latest else 1

        if to_no is None:
            # 최신 회차 자동 탐색
            to_no = self._find_latest_from_page()
            if to_no is None:
                self.stderr.write(self.style.ERROR(
                    '최신 회차를 확인할 수 없습니다.'
                ))
                return

        if from_no > to_no:
            self.stdout.write(self.style.SUCCESS('이미 최신 데이터입니다.'))
            return

        self.stdout.write(f'{from_no}회 ~ {to_no}회 데이터 가져오기...')

        created = 0
        failed = 0

        for draw_no in range(from_no, to_no + 1):
            result = self._fetch_draw(draw_no)
            if result:
                self._save_draw(result)
                created += 1
                self.stdout.write(f'  제{draw_no}회 저장 완료')
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(
                    f'  제{draw_no}회 가져오기 실패'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'완료! 저장: {created}건, 실패: {failed}건'
        ))

    def _get_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'ko-KR,ko;q=0.9',
        })
        return session

    def _fetch_draw(self, draw_no):
        """회차별 당첨 결과 페이지 스크래핑"""
        try:
            session = self._get_session()
            resp = session.get(
                RESULT_URL,
                params={'method': 'byWin', 'drwNo': draw_no},
                timeout=15,
            )
            html = resp.text

            # 회차 번호 확인
            match_no = re.search(r'<strong id="drwNo">(\d+)</strong>', html)
            if not match_no:
                return None

            actual_no = int(match_no.group(1))
            if actual_no != draw_no:
                return None

            # 당첨번호 추출
            numbers = re.findall(
                r'<span id="drwtNo(\d)"[^>]*>(\d+)</span>', html
            )
            if len(numbers) < 6:
                return None

            # 보너스번호
            bonus_match = re.search(
                r'<span id="bnusNo"[^>]*>(\d+)</span>', html
            )
            bonus = int(bonus_match.group(1)) if bonus_match else 0

            # 추첨일
            date_match = re.search(
                r'\((\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*추첨\)', html
            )
            if date_match:
                draw_date = datetime(
                    int(date_match.group(1)),
                    int(date_match.group(2)),
                    int(date_match.group(3)),
                ).date()
            else:
                draw_date = self._estimate_draw_date(draw_no)

            # 1등 당첨금
            prize_match = re.search(
                r'1등.*?<strong[^>]*>([\d,]+)원</strong>', html, re.DOTALL
            )
            first_prize = (
                int(prize_match.group(1).replace(',', ''))
                if prize_match else 0
            )

            # 1등 당첨자수
            winners_match = re.search(
                r'1등.*?(\d+)명', html, re.DOTALL
            )
            first_winners = int(winners_match.group(1)) if winners_match else 0

            # 총판매금액
            sales_match = re.search(
                r'총\s*판매금액.*?([\d,]+)원', html, re.DOTALL
            )
            total_sales = (
                int(sales_match.group(1).replace(',', ''))
                if sales_match else 0
            )

            return {
                'draw_no': draw_no,
                'draw_date': draw_date,
                'numbers': [int(n[1]) for n in sorted(numbers)],
                'bonus': bonus,
                'first_prize': first_prize,
                'first_winners': first_winners,
                'total_sales': total_sales,
            }

        except Exception as e:
            self.stderr.write(f'스크래핑 오류 (제{draw_no}회): {e}')
            return None

    def _save_draw(self, data):
        nums = data['numbers']
        DrawResult.objects.update_or_create(
            draw_no=data['draw_no'],
            defaults={
                'draw_date': data['draw_date'],
                'number_1': nums[0],
                'number_2': nums[1],
                'number_3': nums[2],
                'number_4': nums[3],
                'number_5': nums[4],
                'number_6': nums[5],
                'bonus_number': data['bonus'],
                'first_prize_amount': data['first_prize'],
                'first_prize_winners': data['first_winners'],
                'total_sales': data['total_sales'],
            },
        )

    def _find_latest_from_page(self):
        """메인 결과 페이지에서 최신 회차 확인"""
        try:
            session = self._get_session()
            resp = session.get(
                RESULT_URL,
                params={'method': 'byWin'},
                timeout=15,
            )
            match = re.search(
                r'<strong id="drwNo">(\d+)</strong>', resp.text
            )
            if match:
                return int(match.group(1))
        except Exception as e:
            self.stderr.write(f'최신 회차 확인 오류: {e}')
        return None

    def _estimate_draw_date(self, draw_no):
        from datetime import timedelta
        first_draw = datetime(2002, 12, 7).date()
        return first_draw + timedelta(weeks=draw_no - 1)
