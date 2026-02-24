"""
동행복권 공식 JSON API로 최신 로또 당첨 데이터를 가져오는 커맨드
Usage: python manage.py fetch_latest [--from N] [--to N]
API: https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=N
"""
import json
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from apps.analysis.models import DrawResult

API_URL = 'https://www.dhlottery.co.kr/common.do'


class Command(BaseCommand):
    help = '동행복권 JSON API로 최신 로또 당첨 데이터를 가져옵니다.'

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

        if from_no is None:
            latest = DrawResult.objects.order_by('-draw_no').first()
            from_no = (latest.draw_no + 1) if latest else 1

        if to_no is None:
            to_no = self._find_latest_draw_no()
            if to_no is None:
                self.stderr.write(self.style.ERROR('최신 회차를 확인할 수 없습니다.'))
                return

        if from_no > to_no:
            self.stdout.write(self.style.SUCCESS('이미 최신 데이터입니다.'))
            return

        self.stdout.write(f'{from_no}회 ~ {to_no}회 데이터 가져오기...')

        created = 0
        failed = 0

        for draw_no in range(from_no, to_no + 1):
            data = self._fetch_draw(draw_no)
            if data:
                self._save_draw(data)
                created += 1
                self.stdout.write(f'  제{draw_no}회 저장 완료')
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(f'  제{draw_no}회 가져오기 실패'))

        self.stdout.write(self.style.SUCCESS(f'완료! 저장: {created}건, 실패: {failed}건'))

    def _get_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Referer': 'https://www.dhlottery.co.kr/gameResult.do?method=byWin',
            'X-Requested-With': 'XMLHttpRequest',
        })
        return session

    def _find_latest_draw_no(self):
        """최신 회차 번호 탐색 (이진 탐색으로 빠르게)"""
        session = self._get_session()
        # DB 최신 회차부터 최대 10회 앞까지 시도
        latest_db = DrawResult.objects.order_by('-draw_no').first()
        start = (latest_db.draw_no + 1) if latest_db else 1

        for draw_no in range(start, start + 10):
            data = self._fetch_draw_raw(session, draw_no)
            if data is None:
                return draw_no - 1 if draw_no > start else None
        return start + 9

    def _fetch_draw(self, draw_no):
        session = self._get_session()
        return self._fetch_draw_raw(session, draw_no)

    def _fetch_draw_raw(self, session, draw_no):
        """공식 JSON API 호출"""
        try:
            resp = session.get(
                API_URL,
                params={'method': 'getLottoNumber', 'drwNo': draw_no},
                timeout=15,
            )
            # JSON 응답 파싱
            try:
                data = resp.json()
            except Exception:
                # JSON이 아닌 경우 (HTML 반환 등) → 실패
                return None

            if data.get('returnValue') != 'success':
                return None

            draw_date = datetime.strptime(data['drwNoDate'], '%Y-%m-%d').date()

            return {
                'draw_no': data['drwNo'],
                'draw_date': draw_date,
                'numbers': [
                    data['drwtNo1'], data['drwtNo2'], data['drwtNo3'],
                    data['drwtNo4'], data['drwtNo5'], data['drwtNo6'],
                ],
                'bonus': data['bnusNo'],
                'first_prize': data.get('firstWinamnt', 0),
                'first_winners': data.get('firstPrzwnerCo', 0),
                'total_sales': data.get('totSellamnt', 0),
            }

        except Exception as e:
            self.stderr.write(f'API 오류 (제{draw_no}회): {e}')
            return None

    def _save_draw(self, data):
        nums = sorted(data['numbers'])
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
