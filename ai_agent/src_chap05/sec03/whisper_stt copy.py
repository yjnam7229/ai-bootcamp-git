import os
from dotenv import load_dotenv

import torch
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline 

load_dotenv()
access_tokens = os.getenv("HUGGINGFACE_ACCESS_TOKENS")

# FFmpeg 경로 설정
os.environ["PATH"] += os.pathsep + r"C:\workspaces\ai_agent\src_chap05\ffmpeg\bin"


def whisper_stt(
    audio_file_path: str,       
    output_file_path: str = "./output.csv"
):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, 
        torch_dtype=torch_dtype, 
        low_cpu_mem_usage=True, 
        use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    # 파이프라인 등록
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True, # 청크별로 타임스탬프 반환
        chunk_length_s=10,      # 입력 오디오를 10초씩 나누기
        stride_length_s=2,      # 2초씩 겹치도록 청크 나누기
    )

    result = pipe(audio_file_path)  # 실행 (음성 -> 텍스트화)
    df = whisper_to_dataframe(result, output_file_path)

    return result, df


def whisper_to_dataframe(result, output_file_path):
    start_end_text = []

    for chunk in result["chunks"]:
        start = chunk["timestamp"][0]
        end = chunk["timestamp"][1]
        text = chunk["text"].strip()
        start_end_text.append([start, end, text])
    
    # [수정] 반복문 종료 후 DataFrame 생성 및 CSV 저장 (속도 및 I/O 최적화)
    df = pd.DataFrame(start_end_text, columns=["start", "end", "text"])
    df.to_csv(output_file_path, index=False, sep="|", encoding='utf-8')
    
    return df


# 시간대별로 화자를 구분하는 함수
def speaker_diarization(
    audio_file_path: str,
    output_rttm_file_path: str,
    output_csv_file_path: str
):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=access_tokens
    )

    # CUDA 설정
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        print('cuda is available')
    else:
        print('cuda is not available')
        
    diarization_pipeline = pipeline(audio_file_path)

    # RTTM 파일 출력
    with open(output_rttm_file_path, "w", encoding='utf-8') as rttm:
        diarization_pipeline.write_rttm(rttm)

    # pandas dataframe으로 변환
    df_rttm = pd.read_csv(
        output_rttm_file_path,
        sep=r'\s+',              # [수정] 연속된 공백 구분자 안전하게 처리
        header=None,
        names=['type', 'file', 'chnl', 'start', 'duration', 'C1', 'C2', 'speaker_id', 'C3', 'C4'] 
    )
    
    df_rttm["end"] = df_rttm["start"] + df_rttm["duration"]

    # speaker_id 변경 시점에 그룹 번호(number) 부여
    # [수정] df.at 반복문 대신 pandas shift() 사용하여 그룹화 성능 개선
    df_rttm["number"] = (df_rttm["speaker_id"] != df_rttm["speaker_id"].shift()).cumsum() - 1

    df_rttm_grouped = df_rttm.groupby("number", as_index=False).agg(
        start=pd.NamedAgg(column='start', aggfunc='min'),
        end=pd.NamedAgg(column='end', aggfunc='max'),
        speaker_id=pd.NamedAgg(column='speaker_id', aggfunc='first')
    )

    df_rttm_grouped["duration"] = df_rttm_grouped["end"] - df_rttm_grouped["start"]

    df_rttm_grouped.to_csv(
        output_csv_file_path,
        index=False,
        encoding='utf-8' 
    )
    return df_rttm_grouped


# 음성 텍스트화 + 화자 구분 rttm과 병합
def stt_to_rttm(
    audio_file_path: str, 
    stt_output_file_path: str,
    rttm_file_path: str, 
    rttm_csv_file_path: str, 
    final_output_csv_file_path: str
):
    # 1. whisper 음성 텍스트화
    result, df_stt = whisper_stt(
        audio_file_path,
        stt_output_file_path
    )
    
    # 2. 화자 구분
    df_rttm = speaker_diarization(
        audio_file_path,
        rttm_file_path,
        rttm_csv_file_path
    )

    # 3. 매칭된 텍스트 저장용 리스트 초기화
    rttm_texts = [[] for _ in range(len(df_rttm))]

    # 4. Overlap 수식 수정 및 매칭 진행
    for _, row_stt in df_stt.iterrows():
        stt_start, stt_end = row_stt['start'], row_stt['end']
        
        # 타임스탬프가 None인 경우 예외 처리
        if pd.isna(stt_start) or pd.isna(stt_end):
            continue

        max_overlap = 0
        max_idx = -1

        for i_rttm, row_rttm in df_rttm.iterrows():
            rttm_start, rttm_end = row_rttm['start'], row_rttm['end']
            
            # [수정] 정확한 Overlap 계산식: min(종료시간들) - max(시작시간들)
            overlap = max(0, min(stt_end, rttm_end) - max(stt_start, rttm_start))

            if overlap > max_overlap:
                max_overlap = overlap
                max_idx = i_rttm

        if max_overlap > 0 and max_idx != -1:
            rttm_texts[max_idx].append(str(row_stt['text']))

    # 5. 리스트에 담긴 텍스트들을 줄바꿈문자(\n)로 연결
    df_rttm['text'] = ['\n'.join(texts) for texts in rttm_texts]

    # 6. 최종 파일 저장
    df_rttm.to_csv(
        final_output_csv_file_path,
        index=False,
        sep='|',
        encoding='utf-8'
    ) 

    return df_rttm      


if __name__ == "__main__":
    audio_file_path = "../audio/싼기타_비싼기타.mp3"        # 원본 오디오 파일
    stt_output_file_path = "../audio/싼기타_비싼기타.csv"   # STT 결과 파일
    rttm_file_path = "../audio/싼기타_비싼기타.rttm"        # 화자 분리 원본 파일
    rttm_csv_file_path = "../audio/싼기타_비싼기타_rttm.csv"    # 화자 분리 CSV 파일
    final_csv_file_path = "../audio/싼기타_비싼기타_final.csv"  # 최종 결과 파일

    # 최종 음성 텍스트화 + 화자 구분 rttm 병합 실행
    df_rttm = stt_to_rttm(
        audio_file_path,
        stt_output_file_path,
        rttm_file_path,
        rttm_csv_file_path,
        final_csv_file_path
    )
    print(df_rttm)