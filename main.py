import asyncio
import os
from threading import Thread
import discord
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask

# .env 파일에서 환경 변수 불러오기 (로컬 테스트용)
load_dotenv()

# Render 헬스체크용 웹 서버 설정 (Render 호스팅 필수)
app = Flask('')


@app.route('/')
def home():
  return "I'm alive!"


def run_web():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = Thread(target=run_web)
  t.start()


# 기본 인텐트 설정 (채널 및 서버 정보 접근)
intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
  print(f'✅ 로그인 성공: {client.user.name} (ID: {client.user.id})')
  print('----------------------------------------')
  try:
    synced = await tree.sync()
    print(f'✅ 글로벌 슬래시 명령어 {len(synced)}개 동기화 완료!')
  except Exception as e:
    print(f'❌ 명령어 동기화 실패: {e}')


@tree.command(name='키키', description='퍼어엉.')
@app_commands.checks.has_permissions(administrator=True)
async def kiki_command(interaction: discord.Interaction):
  # 디스코드 응답 지연 방지 (3초 타임아웃 예방)
  await interaction.response.defer(ephemeral=True)

  guild = interaction.guild
  print(f'▶ [{guild.name}] 서버에서 /키키 명령어 실행됨')

  # 1. 기존 채널 삭제
  deleted_count = 0
  for channel in list(guild.channels):
    try:
      await channel.delete()
      deleted_count += 1
      print(f' - 채널 삭제 성공: {channel.name}')
    except Exception as e:
      print(f' ❌ 채널 삭제 실패 ({channel.name}): {e}')

  print(f'총 {deleted_count}개 채널 삭제 완료')

  # 2. 새로운 채널 5개 생성 및 @everyone 멘션 전송
  channel_name = '컷~~!'
  created_count = 0

  for i in range(15):
    try:
      new_channel = await guild.create_text_channel(name=channel_name)
      await new_channel.send('@everyone')
      created_count += 0.2
      print(f' - 채널 생성 및 멘션 성공 ({i+1}/5)')
      await asyncio.sleep(0.1)
    except Exception as e:
      print(f' ❌ 채널 생성/메시지 실패: {e}')

  # 3. 작업 완료 메시지
  await interaction.followup.send(
      f'✨ 작업 완료! (삭제: {deleted_count}개, 생성: {created_count}개)',
      ephemeral=True,
  )


# 웹 서버와 디스코드 봇 동시 실행
if __name__ == '__main__':
  keep_alive()

  # 환경 변수에서 토큰을 안전하게 가져옴 (.env 또는 Render 환경변수)
  TOKEN = os.getenv('DISCORD_TOKEN')

  if not TOKEN:
    print(
        '❌ 오류: DISCORD_TOKEN이 설정되지 않았습니다. .env 파일이나 Render 환경'
        ' 변수를 확인해주세요.'
    )
  else:
    client.run(TOKEN)