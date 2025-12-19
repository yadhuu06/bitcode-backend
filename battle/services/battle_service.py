import logging
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from battle.models import BattleResult
from problems.models import TestCase, Question
from problems.services.judge0_service import verify_with_judge0
from rankings.utils import calculate_elo_1v1, calculate_elo_squad, calculate_elo_team
from room.models import Room

logger = logging.getLogger(__name__)

class BattleService:
    @staticmethod
    def process_submission(user, question_id, room_id, code, language):
        """
        Orchestrates the submission verification process.
        Returns: (data, status_code)
        """
        # 1. Fetch Entities
        question = Question.objects.filter(id=question_id).first()
        if not question:
            return {'error': 'Question not found'}, 404

        room = Room.objects.filter(room_id=room_id).first()
        if not room:
            return {'error': 'Room not found'}, 404

        # 2. Validate Room State
        if not room.start_time:
            return {'error': 'Battle has not started'}, 400

        if room.status == 'completed':
            return {'error': 'Battle has already ended'}, 400

        # 3. Time Limit Check
        if room.time_limit > 0:
            elapsed_minutes = (timezone.now() - room.start_time).total_seconds() / 60
            if elapsed_minutes > room.time_limit:
                BattleService._end_battle_due_to_timeout(room)
                return {'error': 'Time limit exceeded'}, 400

        # 4. Fetch Testcases
        testcases = TestCase.objects.filter(question=question)
        if not testcases.exists():
            return {'error': 'No test cases available'}, 400

        # 5. Verify Code (Judge0)
        verification_result = verify_with_judge0(code, language, testcases)
        if 'error' in verification_result:
            return verification_result, 400

        # 6. Process Success
        if verification_result.get('all_passed'):
            return BattleService._handle_successful_submission(
                user, room, question, verification_result
            )

        return verification_result, 200

    @staticmethod
    def _end_battle_due_to_timeout(room):
        room.status = 'completed'
        room.save()
        
        winners = []
        if BattleResult.objects.filter(room=room).exists():
             winners = BattleResult.objects.filter(room=room).first().results

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"battle_{room.room_id}",
            {
                'type': 'battle_completed',
                'message': 'Battle ended due to time limit',
                'winners': winners,
                'room_capacity': room.capacity
            }
        )

    @staticmethod
    def _handle_successful_submission(user, room, question, verification_result):
        battle_result, _ = BattleResult.objects.get_or_create(
            room=room,
            question=question,
            defaults={'results': []}
        )

        existing_results = battle_result.results
        if any(result['username'] == user.username for result in existing_results):
            return {
                'message': 'You have already submitted a correct solution', 
                'all_passed': True
            }, 200

        position = len(existing_results) + 1
        battle_result.add_participant_result(
            user=user,
            position=position,
            completion_time=timezone.now()
        )
        verification_result['position'] = position

        # Elo Calculation
        if room.is_ranked:
            if room.capacity == 2:
                calculate_elo_1v1(room.room_id, winner_id=user.user_id)
            elif 3 <= room.capacity <= 5:
                calculate_elo_squad(room)
            elif room.capacity >= 6:
                calculate_elo_team(room)

        # Update User Stats
        if position == 1:
            user.battles_won += 1
            user.last_win = timezone.now().date()
            user.save()

        # Check for Battle End
        max_winners = {2: 1, 5: 2, 10: 3}.get(room.capacity, 1)
        
        channel_layer = get_channel_layer()
        if len(existing_results) + 1 >= max_winners:
            room.status = 'completed'
            room.save()
            
            async_to_sync(channel_layer.group_send)(
                f"battle_{room.room_id}",
                {
                    'type': 'battle_completed',
                    'user': user.username,
                    'question_id': str(question.id),
                    'winners': battle_result.results[:max_winners],
                    'room_capacity': room.capacity,
                    'message': 'Battle Ended!'
                }
            )
        else:
            async_to_sync(channel_layer.group_send)(
                f"battle_{room.room_id}",
                {
                    'type': 'code_verified',
                    'username': user.username,
                    'position': position,
                    'completion_time': timezone.now().isoformat()
                }
            )

        return verification_result, 200
