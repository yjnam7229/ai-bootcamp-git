/*Ch08 예제*/
/*예제8-1*/
CREATE DATABASE 한빛학사;

/*예제8-2*/
CREATE TABLE 학과 (
     학과번호 CHAR(2)
    ,학과명 VARCHAR(20)
    ,학과장명 VARCHAR(20)
);

INSERT INTO 학과 
VALUES ('AA','컴퓨터공학과','배경민')
      ,('BB','소프트웨어학과','김남준')
      ,('CC','디자인융합학과','박선영');
      
SELECT * FROM 한빛학사.학과;     

/*예제8-3*/
CREATE TABLE 학생( 
     학번 CHAR(5)
    ,이름 VARCHAR(20) 
    ,생일 DATE
    ,연락처 VARCHAR(20)
    ,학과번호 CHAR(2)
);

INSERT INTO 학생 
VALUES ('S0001','이윤주','2020-01-30','01033334444','AA')
	  ,('S0001','이승은',
      '2021-02-23', NULL,'AA')
      ,('S0003','백재용','2018-03-31','01077778888','DD');

SELECT * FROM 한빛학사.학생;   

/*예제8-4*/
CREATE TABLE 휴학생 AS
SELECT *
FROM 학생
WHERE 1 = 2; -- WHERE 1 = 2 : 거짓이 되므로 데이터 까지는 복사 하지 않는다(HEAD의 정보 복사), 데이터 까지 그대로 복사 WHERE 1 = 1

SELECT * FROM 한빛학사.휴학생;   

/*예제8-5*/
CREATE TABLE 회원 (
     아이디 VARCHAR(20) PRIMARY KEY
    ,회원명 VARCHAR(20)
    ,키 INT
    ,몸무게 INT
    ,체질량지수 DECIMAL(4,1) AS (몸무게 / POWER(키 / 100, 2)) STORED
);
    
INSERT INTO 회원(아이디, 회원명, 키, 몸무게)
VALUES('APPLE','김사과',178, 70);

SELECT * FROM 한빛학사.회원;   

/*예제8-6*/
ALTER TABLE 한빛학사.학생 ADD 성별 CHAR(1);

/*예제8-7*/
ALTER TABLE 학생 MODIFY COLUMN 성별 VARCHAR(2);
desc 학생;

/*예제8-8*/
ALTER TABLE 학생 CHANGE COLUMN 연락처 휴대폰번호 VARCHAR(20);

/*예제8-9*/
ALTER TABLE 학생 DROP COLUMN 성별;

/*예제8-10*/
ALTER TABLE 휴학생 RENAME 졸업생;
SELECT * FROM 졸업생;   


/*예제8-11*/
DROP TABLE 학과;
DROP TABLE 학생;

-- 제약조건
/*예제8-12*/
/*방법1*/
CREATE TABLE 학과
    (
       학과번호 CHAR(2) PRIMARY KEY
      ,학과명 VARCHAR(20) NOT NULL
      ,학과장명 VARCHAR(20)
    );

/*방법2*/
CREATE TABLE 학과
    (
       학과번호 CHAR(2)
      ,학과명 VARCHAR(20) NOT NULL
      ,학과장명 VARCHAR(20)
      ,PRIMARY KEY(학과번호)
    );
    
/*예제8-13*/
/*방법1*/
CREATE TABLE 학생
    (
       학번 CHAR(5) PRIMARY KEY
      ,이름 VARCHAR(20) NOT NULL
      ,생일 DATE NOT NULL
      ,연락처 VARCHAR(20) UNIQUE
      ,학과번호 CHAR(2) REFERENCES 학과(학과번호)
      ,성별 CHAR(1) CHECK(성별 IN ('남','여'))
      ,등록일 DATE DEFAULT(CURDATE())
      ,FOREIGN KEY (학과번호) REFERENCES 학과(학과번호)
    );

/*방법2*/
CREATE TABLE 학생
    (
       학번 CHAR(5)
      ,이름 VARCHAR(20) NOT NULL
      ,생일 DATE NOT NULL
      ,연락처 VARCHAR(20)
      ,학과번호 CHAR(2)
      ,성별 CHAR(1)
      ,등록일 DATE DEFAULT(CURDATE())
      ,PRIMARY KEY(학번)
      ,UNIQUE(연락처)
      ,CHECK(성별 IN ('남','여'))
      ,FOREIGN KEY (학과번호) REFERENCES 학과(학과번호)
    );

/*예제8-14*/
CREATE TABLE 과목
    (
	   과목번호 CHAR(5) PRIMARY KEY
      ,과목명 VARCHAR(20) NOT NULL
      ,학점 INT NOT NULL CHECK(학점 BETWEEN 2 AND 4)
      ,구분 VARCHAR(20) CHECK(구분 IN ('전공','교양','일반'))
    );

/*예제8-15*/
CREATE TABLE 수강_1
    (
       수강년도 CHAR(4) NOT NULL
      ,수강학기 VARCHAR(20) NOT NULL
                  CHECK(수강학기 IN ('1학기','2학기','여름학기','겨울학기'))
      ,학번 CHAR(5) NOT NULL
      ,과목번호 CHAR(5) NOT NULL
      ,성적 NUMERIC(3,1) CHECK(성적 BETWEEN 0 AND 4.5)
      ,PRIMARY KEY(수강년도, 수강학기, 학번, 과목번호) -- 복합키
      ,FOREIGN KEY (학번) REFERENCES 학생(학번) -- 외래키 제약조건, 학생 테이블의 학번 데이터가 존재 여부를 검토해서 존재하지 않으면 에러 발생
      ,FOREIGN KEY (과목번호) REFERENCES 과목(과목번호)
    );

/*예제8-16*/
CREATE TABLE 수강_2
    (
       수강번호 INT PRIMARY KEY AUTO_INCREMENT
      ,수강년도 CHAR(4) NOT NULL
      ,수강학기 VARCHAR(20) NOT NULL
                  CHECK(수강학기 IN ('1학기','2학기','여름학기','겨울학기'))
      ,학번 CHAR(5) NOT NULL
      ,과목번호 CHAR(5) NOT NULL
      ,성적 NUMERIC(3,1) CHECK(성적 BETWEEN 0 AND 4.5)
      ,FOREIGN KEY (학번) REFERENCES 학생(학번)
      ,FOREIGN KEY (과목번호) REFERENCES 과목(과목번호)
    );

/*예제8-17*/
INSERT INTO 학과
VALUES ('AA','컴퓨터공학과','배경민');

INSERT INTO 학과
VALUES ('AA','소프트웨어학과','김남준'); -- Duplicate entry 'AA' for key '학과.PRIMARY' 


INSERT INTO 학과
VALUES ('CC','디자인융합학과','박선영');

/*오류 수정*/
INSERT INTO 학과
VALUES ('BB','소프트웨어학과','김남준');

/*예제8-18*/
INSERT INTO 학생(학번, 이름, 생일, 학과번호) 
VALUES ('S0001','이윤주','2020-01-30','AA');

INSERT INTO 학생(이름, 생일, 학과번호) 
VALUES ('이승은','2021-02-23','AA');   -- Error Code: 1364. Field '학번' doesn't have a default value 

SELECT * FROM 학과;
INSERT INTO 학생(학번, 이름, 생일, 학과번호) 
VALUES ('S0003','백재용','2018-03-31','DD'); 
-- Cannot add or update a child row: a foreign key constraint fails (`한빛학사`.`학생`, CONSTRAINT `학생_ibfk_1` FOREIGN KEY (`학과번호`) REFERENCES `학과` (`학과번호`)) 
-- 학과 테이블에 없는 'DD' 데이터를 삽입 시 에러 발생, 학생 테이블의 학과번호는 외래키로 정의

/*오류 수정*/
INSERT INTO 학생(학번, 이름, 생일, 학과번호)
VALUES ('S0002', '이승은','2020-01-30', 'AA');

INSERT INTO 학생(학번, 이름, 생일, 학과번호)
VALUES ('S0003','백재용','2018-03-31','CC');

/*예제8-19*/
INSERT INTO 과목(과목번호, 과목명, 구분)
VALUES ('C0001','데이터베이스실습', '전공'); -- 학점은 NOT NULL 속성

INSERT INTO 과목(과목번호, 과목명, 구분, 학점)
VALUES ('C0002','데이터베이스 설계와 구축', '전공', 5);  -- CHECK (학점 between 2 and 4)

INSERT INTO 과목(과목번호, 과목명, 구분, 학점)
VALUES ('C0003','데이터 분석', '전공', 3);

/*오류 수정*/
INSERT INTO 과목(과목번호, 과목명, 구분, 학점)
VALUES ('C0001','데이터베이스실습', '전공', 3);

INSERT INTO 과목(과목번호, 과목명, 구분, 학점)
VALUES ('C0002','데이터베이스 설계와 구축', '전공', 3);

/*예제8-20*/
INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0001', 4.3);

INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0001', 4.5);

INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0002', 4.6);  -- CHECK (성적 between 0 and 4.5)

SELECT * FROM 과목;
INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0002','C0009', 4.3);  -- 과목 테이블에 없는 'C0009' 데이터를 삽입 시 에러 발생, 수강_1 테이블의 과목번호는 외래키로 정의

/*오류 수정*/
INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0002', 4.4);

INSERT INTO 수강_1(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0002','C0002', 4.3);

/*예제8-21*/
INSERT INTO 수강_2(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0001', 4.3);

INSERT INTO 수강_2(수강년도, 수강학기, 학번, 과목번호, 성적)
VALUES('2023','1학기','S0001','C0001', 4.5);

/*예제8-22*/
ALTER TABLE 학생 ADD CONSTRAINT CHECK(학번 LIKE 'S%');  -- 제약조건 추가 수정
desc 학생;

/*예제8-23*/
SELECT *
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = '한빛학사'
AND TABLE_NAME = '학생';

/*예제8-24*/
ALTER TABLE 학생 DROP CONSTRAINT 연락처;

/*예제8-25*/
ALTER TABLE 학생 DROP CONSTRAINT 학생_chk_1;

ALTER TABLE 학생 DROP CONSTRAINT 학생_chk_2;

ALTER TABLE 학생 ADD CHECK (학번 LIKE 'S%');

/*예제8-26*/
CREATE TABLE 학생_2 (
    학번 CHAR(5),
    이름 VARCHAR(20) NOT NULL,
    생일 DATE NOT NULL,
    연락처 VARCHAR(20),
    학과번호 CHAR(2),
    성별 CHAR(1),
    등록일 DATE DEFAULT(CURDATE()),
    PRIMARY KEY(학번),
    CONSTRAINT UK_학생2_연락처 UNIQUE(연락처),
    CONSTRAINT CK_학생2_성별 CHECK(성별 IN ('남','여')),
    CONSTRAINT FK_학생2_학과번호 FOREIGN KEY (학과번호) REFERENCES 학과(학과번호)
);

SELECT *
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = '한빛학사'
AND TABLE_NAME = '학생_2';

/*예제8-27*/
-- 부모 레코드 삭제 시 자식 레코드도 연쇄적으로 삭제 CASCADE
CREATE TABLE 수강평가 (
    평가번호 INT PRIMARY KEY AUTO_INCREMENT,
    학번 CHAR(5) NOT NULL,
    과목번호 CHAR(5) NOT NULL,
    평점 INT CHECK(평점 BETWEEN 0 AND 5),
    과목평가 VARCHAR(500),
    평가일시 DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (학번) REFERENCES 학생(학번),
    FOREIGN KEY (과목번호) REFERENCES 과목(과목번호) ON DELETE CASCADE  -- 수강평가의 과목번호는 과목 테이블의 과목번호를 참조  
);

SELECT * FROM 수강평가;
SELECT * FROM 과목;
/*예제8-28*/
INSERT INTO 수강평가(학번, 과목번호, 평점, 과목평가)
VALUES('S0001','C0001',5,'SQL학습에 도움이 되었습니다.'),
      ('S0001','C0003',5,'SQL 활용을 배워서 좋았습니다.'),
      ('S0002','C0003',5,'데이터 분석에 관심이 생겼습니다.'),
      ('S0003','C0003',5,'머신러닝과 시각화 부분이 유용했습니다.');

/*예제8-29*/
DELETE FROM 과목 WHERE 과목번호 = 'C0003';

SELECT * FROM 과목;
SELECT * FROM 수강평가;

/*예제8-30*/
DELETE FROM 과목 WHERE 과목번호 = 'C0001';
-- Cannot delete or update a parent row: a foreign key constraint fails (`한빛학사`.`수강_1`, CONSTRAINT `수강_1_ibfk_2` FOREIGN KEY (`과목번호`) REFERENCES `과목` (`과목번호`)) 

