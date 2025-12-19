import logging
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from problems.models import Question, TestCase, SolvedCode, Example
from problems.serializers import QuestionListSerializer, TestCaseSerializer, ExampleSerializer
from problems.utils import extract_function_name_and_params
from battle.models import UserRanking
from battle.services.battle_service import BattleService

logger = logging.getLogger(__name__)


class BattleQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        try:
            question = get_object_or_404(Question, id=question_id)
            if not question:
                logger.error(f"Question not found: {question_id}")
                return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = QuestionListSerializer(question)
            testcases = TestCase.objects.filter(question=question)
            example = Example.objects.filter(question=question)
            example_formatted = ExampleSerializer(example, many=True)
            testcase_serializer = TestCaseSerializer(testcases, many=True)

            solved_code = SolvedCode.objects.filter(question=question, language='python').first()
            function_details = {'function_name': '', 'parameters': []}
            
            if solved_code:
                try:
                    extracted_details = extract_function_name_and_params(solved_code.solution_code, 'python')
                    function_details = {
                        'function_name': extracted_details.get('name', ''),
                        'parameters': extracted_details.get('params', [])
                    }
                except Exception as e:
                    logger.warning(f"Failed to extract function details for question {question_id}: {str(e)}")

            logger.info(f"Fetched battle question {question_id}: {question.title}")
            return Response({
                'question': serializer.data,
                'testcases': testcase_serializer.data,
                'example': example_formatted.data,
                'function_details': function_details
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching battle question {question_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionVerifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        code = request.data.get('code')
        language = request.data.get('language')
        room_id = request.data.get('room_id')

        logger.info(f"Room ID received: {room_id}")

        if not all([code, language, room_id]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Delegate all logic to the BattleService
            data, status_code = BattleService.process_submission(
                user=request.user,
                question_id=question_id,
                room_id=room_id,
                code=code,
                language=language
            )
            return Response(data, status=status_code)

        except Exception as e:
            logger.error(f"Error verifying code for question {question_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class GlobalRankingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):  
        rankings = UserRanking.objects.select_related('user').order_by('-points')[:100]
        ranking_data = []
        
        for index, rank in enumerate(rankings, start=1):
            ranking_data.append({
                'rank': index,
                'username': rank.user.username,
                'points': rank.points
            })

        return Response(ranking_data)