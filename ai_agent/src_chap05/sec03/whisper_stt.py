import os
from dotenv import load_dotenv

import torch
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline 

load_dotenv()
access_tokens = os.getenv("HUGGINGFACE_ACCESS_TOKENS")

os.environ["PATH"] += os.pathsep + r"C:\workspaces\ai_agent\src_chap05\ffmpeg\bin"

def whisper_stt(
    audio_file_path: str,      
    output_file_path: str = "./output.csv"
):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(  # 다운로드 기능 from_pretrained
        model_id, torch_dtype=torch_dtype, 
        low_cpu_mem_usage=True, 
        use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id) # 도구 다운로드

    # 파이프라인 등록
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True, # 청크별로 타임스탬프를 반환
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
        df = pd.DataFrame(start_end_text, columns=["start", "end", "text"])
        df.to_csv(output_file_path, index=False, sep="|")
    
    return df

# 시간대별로 화자를 구분하는 함수
def speaker_diarization(
        audio_file_path: str,
        output_rttm_file_path: str,
        output_csv_file_path: str
    ):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",  # HuggigFace 화자 분리 모델
        use_auth_token=access_tokens
    )

    # cuda가 사용 가능한 경우 cuda를 사용하도록 설정
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        print('cuda is available')
    else:
        print('cuda is not available')
    diarization_pipeline = pipeline(audio_file_path)

    # dump the diarization output to disk using RTTM format
    with open(output_rttm_file_path, "w", encoding='utf-8') as rttm:
        diarization_pipeline.write_rttm(rttm)

    # pandas dataframe으로 변환
    df_rttm = pd.read_csv(
        output_rttm_file_path,  # rttm 파일 경로
        sep=' ',                # 구분자는 띄어쓰기
        header=None,            # 헤더는 없음
        names=['type', 'file', 'chnl', 'start', 'duration', 'C1', 'C2', 'speaker_id', 'C3', 'C4'] 
    )
    
    df_rttm["end"] = df_rttm["start"] + df_rttm["duration"]

    # speaker_id를 기반으로 화자별로 구간을 나누기
    df_rttm["number"] = None
    df_rttm.at[0, "number"] = 0

    for i in range(1, len(df_rttm)):
        if df_rttm.at[i, "speaker_id"] != df_rttm.at[i-1, "speaker_id"]:
            df_rttm.at[i, "number"] = df_rttm.at[i-1, "number"] + 1
        else:
            df_rttm.at[i, "number"] = df_rttm.at[i-1, "number"]

    df_rttm_grouped = df_rttm.groupby("number").agg(
        start=pd.NamedAgg(column='start', aggfunc='min'),
        end=pd.NamedAgg(column='end', aggfunc='max'),
        speaker_id=pd.NamedAgg(column='speaker_id', aggfunc='first')
    )

    df_rttm_grouped["duration"] = df_rttm_grouped["end"] - df_rttm_grouped["start"]

    df_rttm_grouped.to_csv(
        output_csv_file_path,
        index=False,    # 인덱스는 저장하지 않음
        encoding='utf-8' 
    )
    return df_rttm_grouped


# 음성 텍스트화 + 화자 구분 rttm과 병합
def stt_to_rttm(
    audio_file_path: str, 
    stt_output_file_path: str,
    rttm_file_path: str,    # speaker diarization 모델
    rttm_csv_file_path: str, 
    final_output_csv_file_path: str
):
    # whisper가 음성 텍스트화
    result, df_stt = whisper_stt(
        audio_file_path,
        stt_output_file_path
    )
    #  화자 구분
    df_rttm = speaker_diarization(
        audio_file_path,
        rttm_file_path,
        rttm_csv_file_path
    )

    df_rttm['text'] = '' # 대화 내용

    for i_stt, row_stt in df_stt.iterrows():   # 현재 whisper의 결과 데이터, 화자가 없고 timestamp만 있음, iterrows : 행별 인덱스, 데이터를 가져옴
        overlap_dict = {}
        for i_rttm, row_rttm in df_rttm.iterrows():  # 화자 diarzation 데이터 
            overlap = max(0, min(row_stt['end'], row_rttm['end']) - max(row_stt['start'], row_rttm['start']))
            overlap_dict[i_rttm] = overlap

        max_overlap = max(overlap_dict.values())
        max_overlap_idx = max(overlap_dict, key=overlap_dict.get)

        if max_overlap > 0:
            df_rttm.at[max_overlap_idx, 'text'] += row_stt['text']  + '\n'     # 음수이면 겹침이 없음 -> 텍스트가 삽입되어져야 할 인덱스 위치값

    df_rttm.to_csv(
        final_output_csv_file_path,
        index=False,
        sep='|',
        encoding='utf-8'
    ) 

    return df_rttm      

#  __main__함수
if __name__ == "__main__":
    audio_file_path = "../audio/싼기타_비싼기타.mp3"        # 원본 오디오 파일
    stt_output_file_path = "../audio/싼기타_비싼기타.csv"   # STT 결과 파일
    rttm_file_path = "../audio/싼기타_비싼기타.rttm"        # 화자 분리 원본 파일
    rttm_csv_file_path = "../audio/싼기타_비싼기타_rttm.csv"    # 화자 분리 CSV 파일
    final_csv_file_path = "../audio/싼기타_비싼기타_final.csv"  # 최종 결과 파일

    # whisper 구동 : 음성 -> 텍스트화
    # result, df = whisper_stt(
    #     audio_file_path, 
    #     stt_output_file_path
    # )
    # print(df)

    # 시간대별로 화자를 구분하는 함수
    # df_rttm = speaker_diarization(
    #     audio_file_path,
    #     rttm_file_path,
    #     rttm_csv_file_path
    # )
    # print(df_rttm)

    # 최종 음성 텍스트화 + 화자 구분 rttm과 병합
    df_rttm = stt_to_rttm(
        audio_file_path,
        stt_output_file_path,
        rttm_file_path,
        rttm_csv_file_path,
        final_csv_file_path
    )
    print(df_rttm)

