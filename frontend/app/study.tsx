import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  FlatList,
  ListRenderItem,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useEffect, useState, useRef } from "react";
import { useRouter, useLocalSearchParams } from "expo-router";
import * as Clipboard from 'expo-clipboard';
import Feather from '@expo/vector-icons/Feather';
import Ionicons from '@expo/vector-icons/Ionicons';
import { articleAPI, translationAPI } from "../services/api";

interface Sentence {
  id: string;
  text: string;
}

interface Article {
  id: string;
  title: string;
  sentences: Sentence[];
}

interface Attempt {
  input: string;
  feedback: string;
  isCorrect: boolean;
  result: 'perfect' | 'good' | 'incorrect';
}

interface SentenceHistory {
  attempts: Attempt[];
  status: 'perfect' | 'good' | 'incorrect' | 'skipped' | null;
}

export default function StudyScreen() {
  const router = useRouter();
  const { articleId } = useLocalSearchParams<{ articleId: string }>();

  const [article, setArticle] = useState<Article | null>(null);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState<number>(0);
  const [userTranslation, setUserTranslation] = useState<string>("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [result, setResult] = useState<'perfect' | 'good' | 'incorrect' | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [checking, setChecking] = useState<boolean>(false);

  const [sentenceHistory, setSentenceHistory] = useState<Record<string, SentenceHistory>>({});
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [copiedSentenceId, setCopiedSentenceId] = useState<string | null>(null);

  const currentSentenceRef = useRef<View>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const articleScrollRef = useRef<FlatList<Sentence>>(null);
  const currentScrollY = useRef<number>(0);

  // 아이템 높이와 누적 오프셋 저장
  const heights = useRef<number[]>([]);
  const offsets = useRef<number[]>([]);
  const viewportHeight = useRef<number>(0);

  useEffect(() => {
    loadArticle();
  }, [articleId]);

  const loadArticle = async () => {
    try {
      setLoading(true);
      const data = await articleAPI.getById(articleId);
      setArticle(data);
    } catch (err) {
      console.error("Failed to load article:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!userTranslation.trim() || !article) return;

    const currentSentence = article.sentences[currentSentenceIndex];

    try {
      setChecking(true);
      setFeedback(null);
      setIsCorrect(null);

      const response = await translationAPI.check(
        currentSentence.id,
        userTranslation
      );

      setIsCorrect(response.is_correct);
      setFeedback(response.feedback);
      setResult(response.result as 'perfect' | 'good' | 'incorrect');

      // 시도 기록 저장
      const sentenceId = currentSentence.id;
      const newAttempt: Attempt = {
        input: userTranslation,
        feedback: response.feedback || '',
        isCorrect: response.is_correct,
        result: response.result as 'perfect' | 'good' | 'incorrect',
      };

      setSentenceHistory(prev => {
        const history = prev[sentenceId] || { attempts: [], status: null };
        const updatedAttempts = [...history.attempts, newAttempt];

        // 상태 결정: result 필드 활용
        let status = history.status;
        if (response.result === 'perfect') {
          status = 'perfect';
        } else if (response.result === 'good') {
          status = 'good';
        } else if (response.result === 'incorrect') {
          status = 'incorrect';
        }

        return {
          ...prev,
          [sentenceId]: { attempts: updatedAttempts, status }
        };
      });

      // perfect 또는 good이면 다음 문장으로 이동
      if (response.result === 'perfect' || response.result === 'good') {
        setTimeout(() => {
          moveToNextSentence();
        }, 2000);
      }
    } catch (err) {
      console.error("Failed to check translation:", err);
      setFeedback("Error checking translation. Please try again.");
      setIsCorrect(false);
    } finally {
      setChecking(false);
    }
  };

  const onItemLayout = (index: number, height: number) => {
    if (!article) return;

    heights.current[index] = height;

    // 해당 인덱스부터 끝까지 오프셋 재계산
    let cumulativeOffset = 0;
    for (let i = 0; i <= index; i++) {
      if (heights.current[i] !== undefined) {
        cumulativeOffset += heights.current[i];
      }
    }
    offsets.current[index] = cumulativeOffset;

    // 이후 아이템들도 오프셋 업데이트
    for (let i = index + 1; i < article.sentences.length; i++) {
      if (heights.current[i] !== undefined) {
        cumulativeOffset += heights.current[i];
        offsets.current[i] = cumulativeOffset;
      }
    }
  };

  const scrollToItemIfNeeded = (index: number) => {
    const viewTop = currentScrollY.current;
    const viewBottom = viewTop + viewportHeight.current;

    const top = offsets.current[index - 1] || 0;
    const bottom = top + heights.current[index];

    let newScrollY = currentScrollY.current;

    // 위쪽이 잘린 경우: 위로 스크롤
    if (top < viewTop) {
      newScrollY = top;
    }
    // 아래쪽이 잘린 경우: 아래로 스크롤
    else if (bottom > viewBottom) {
      newScrollY = bottom - viewportHeight.current;
    }
    // 다 보이는 경우: 스크롤 안 함
    else {
      // console.log(`Item ${index} is fully visible, no scroll needed`);
      return;
    }

    // console.log(`Scrolling from ${currentScrollY.current} to ${newScrollY}`);
    articleScrollRef.current?.scrollToOffset({
      offset: newScrollY,
      animated: true,
    });
  };

  const moveToNextSentence = () => {
    if (!article) return;

    if (currentSentenceIndex < article.sentences.length - 1) {
      const nextIndex = currentSentenceIndex + 1;
      setCurrentSentenceIndex(nextIndex);
      setUserTranslation("");
      setFeedback(null);
      setIsCorrect(null);
      setResult(null);
      setTimeout(() => scrollToItemIfNeeded(nextIndex), 100);
    } else {
      // setCurrentSentenceIndex(0);
      // setTimeout(() => scrollToItemIfNeeded(0), 100);
      router.replace("/result");
    }
  };


  const handleSkip = () => {
    if (!article) return;

    const currentSentence = article.sentences[currentSentenceIndex];

    // 제출 이력이 있는 경우 상태 유지, 없는 경우만 'skipped'로 설정
    setSentenceHistory(prev => {
      const existingHistory = prev[currentSentence.id];
      const hasAttempts = existingHistory?.attempts?.length > 0;

      return {
        ...prev,
        [currentSentence.id]: {
          attempts: existingHistory?.attempts || [],
          status: hasAttempts ? existingHistory.status : 'skipped'
        }
      };
    });

    moveToNextSentence();
  };

  const handleSentenceClick = (index: number) => {
    setCurrentSentenceIndex(index);
    setUserTranslation("");
    setFeedback(null);
    setIsCorrect(null);
    setResult(null);
    setShowHistory(false); // 문장 변경 시 이전 시도 접기

    // console.log(`Selected item ${index}: height=${heights.current[index]}, offset=${offsets.current[index]}`);
    // console.log(`Current scrollY: ${currentScrollY.current}, viewportHeight: ${viewportHeight.current}`);

    scrollToItemIfNeeded(index);
  };

  const handleShowAnswer = () => {
    // TODO: 백엔드에 정답 번역 필드 추가 후 구현
    setFeedback("정답 보기 기능은 곧 추가될 예정입니다.");
  };

  const handleCopy = async (sentenceId: string, text: string) => {
    await Clipboard.setStringAsync(text);
    setCopiedSentenceId(sentenceId);
    setTimeout(() => setCopiedSentenceId(null), 2000);
  };

  const renderSentence: ListRenderItem<Sentence> = ({ item: sentence, index }) => {
    const history = sentenceHistory[sentence.id];
    const status = history?.status;

    return (
      <View key={sentence.id}>
        <TouchableOpacity
          onPress={() => handleSentenceClick(index)}
          activeOpacity={0.7}
          onLayout={(e) => {
            const { height } = e.nativeEvent.layout;
            onItemLayout(index, height);
          }}
        >
          <View
            ref={index === currentSentenceIndex ? currentSentenceRef : null}
            style={[
              styles.sentenceContainer,
              index === currentSentenceIndex && styles.currentSentence,
            ]}
          >
            <View style={styles.sentenceRow}>
              {status && (
                <View
                  style={[
                    styles.statusDot,
                    status === 'perfect' && styles.statusPerfect,
                    status === 'good' && styles.statusGood,
                    status === 'incorrect' && styles.statusIncorrect,
                    status === 'skipped' && styles.statusSkipped,
                  ]}
                />
              )}
              <Text
                style={[
                  styles.sentenceText,
                  index === currentSentenceIndex && styles.currentSentenceText,
                ]}
              >
                {sentence.text}
              </Text>

              <TouchableOpacity
                onPress={(e) => {
                  e.stopPropagation();
                  handleCopy(sentence.id, sentence.text);
                }}
                style={styles.copyButton}
              >
                {copiedSentenceId === sentence.id ? (
                  <Ionicons name="checkmark-outline" size={14} color="#34C759" />
                ) : (
                  <Feather name="copy" size={14} color="#999" />
                )}
              </TouchableOpacity>
            </View>
          </View>
        </TouchableOpacity>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!article || !article.sentences || article.sentences.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>No sentences found</Text>
      </View>
    );
  }

  const currentSentence = article.sentences[currentSentenceIndex];
  const progress = ((currentSentenceIndex + 1) / article.sentences.length) * 100;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <ScrollView ref={scrollViewRef} contentContainerStyle={styles.scrollContent}>
        <View style={styles.progressContainer}>
          <View style={[styles.progressBar, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>
          {currentSentenceIndex + 1} / {article.sentences.length}
        </Text>

        <Text style={styles.articleTitle}>{article.title}</Text>

        <View style={styles.articleContent}>
          <Text style={styles.contentLabel}>Article (tap to navigate)</Text>
          <FlatList
            ref={articleScrollRef}
            style={styles.articleScroll}
            data={article.sentences}
            renderItem={renderSentence}
            keyExtractor={(item) => item.id}
            nestedScrollEnabled={true}
            scrollEventThrottle={16}
            onScroll={(e) => {
              currentScrollY.current = e.nativeEvent.contentOffset.y;
            }}
            onLayout={(e) => {
              viewportHeight.current = e.nativeEvent.layout.height;
            }}
          />
        </View>

        {/* 현재 문장의 시도 기록 표시 */}
        {sentenceHistory[currentSentence?.id]?.attempts?.length > 0 && (
          <View style={styles.historyContainer}>
            <TouchableOpacity
              onPress={() => setShowHistory(!showHistory)}
              style={styles.historyHeader}
            >
              <Text style={styles.historyLabel}>
                이전 시도 ({sentenceHistory[currentSentence.id].attempts.length}회)
              </Text>
              <Text style={styles.historyToggle}>
                {showHistory ? "▼" : "▶"}
              </Text>
            </TouchableOpacity>

            {showHistory && (
              <View style={styles.historyContent}>
                {sentenceHistory[currentSentence.id].attempts.map((attempt, idx) => (
                  <View key={idx} style={styles.historyItem}>
                    <Text style={styles.historyInput}>→ {attempt.input}</Text>
                    <View style={styles.historyFeedbackRow}>
                      <View style={[
                        styles.historyResultBadge,
                        attempt.result === 'perfect' && styles.historyResultPerfect,
                        attempt.result === 'good' && styles.historyResultGood,
                        attempt.result === 'incorrect' && styles.historyResultIncorrect,
                      ]}>
                        <Text style={styles.historyResultText}>
                          {attempt.result === 'perfect' ? 'Perfect' :
                           attempt.result === 'good' ? 'Good' : 'Incorrect'}
                        </Text>
                      </View>
                      <Text
                        style={[
                          styles.historyFeedback,
                          attempt.result === 'perfect' && styles.historyFeedbackPerfect,
                          attempt.result === 'good' && styles.historyFeedbackGood,
                        ]}
                      >
                        {attempt.feedback}
                      </Text>
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        <View style={styles.inputContainer}>
          <Text style={styles.inputLabel}>한국어로 번역하세요</Text>
          <TextInput
            style={[
              styles.input,
              isCorrect === true && styles.inputCorrect,
              isCorrect === false && styles.inputIncorrect,
            ]}
            value={userTranslation}
            onChangeText={setUserTranslation}
            placeholder="번역을 입력하세요..."
            multiline
            numberOfLines={3}
            editable={!checking && isCorrect !== true}
          />
        </View>

        {feedback && (
          <View
            style={[
              styles.feedbackCard,
              isCorrect ? styles.feedbackCorrect : styles.feedbackIncorrect,
            ]}
          >
            <Text style={styles.feedbackText}>{feedback}</Text>
          </View>
        )}

        {isCorrect === true && (
          <View style={[
            styles.feedbackCard,
            result === 'perfect' && styles.feedbackPerfect,
            result === 'good' && styles.feedbackGood,
          ]}>
            {result === 'perfect' && (
              <>
                <Text style={styles.correctText}>✓ Perfect!</Text>
                <Text style={styles.correctSubtext}>완벽합니다! Moving to next sentence...</Text>
              </>
            )}
            {result === 'good' && (
              <>
                <Text style={styles.correctText}>✓ Good!</Text>
                <Text style={styles.correctSubtext}>좋습니다! Moving to next sentence...</Text>
              </>
            )}
          </View>
        )}

        <View style={styles.buttonContainer}>
          {isCorrect !== true && (
            <>
              <View style={styles.actionRow}>
                <TouchableOpacity
                  style={[styles.button, styles.submitButton, { flex: 2 }]}
                  onPress={handleSubmit}
                  disabled={checking || !userTranslation.trim()}
                >
                  {checking ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.buttonText}>Submit</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.button, styles.skipButton, { flex: 1 }]}
                  onPress={handleSkip}
                  disabled={checking}
                >
                  <Text style={styles.skipButtonText}>Skip</Text>
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={[styles.button, styles.answerButton]}
                onPress={handleShowAnswer}
                disabled={checking}
              >
                <Text style={styles.answerButtonText}>Show Answer</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  centerContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
  },
  scrollContent: {
    padding: 20,
    paddingTop: 60,
  },
  progressContainer: {
    height: 4,
    backgroundColor: "#e0e0e0",
    borderRadius: 2,
    marginBottom: 8,
    overflow: "hidden",
  },
  progressBar: {
    height: "100%",
    backgroundColor: "#007AFF",
    borderRadius: 2,
  },
  progressText: {
    fontSize: 14,
    color: "#666",
    textAlign: "right",
    marginBottom: 16,
  },
  articleTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 24,
  },
  articleContent: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 12,
    marginBottom: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  articleScroll: {
    maxHeight: 300,
  },
  contentLabel: {
    fontSize: 12,
    color: "#999",
    textTransform: "uppercase",
    marginBottom: 16,
    fontWeight: "600",
  },
  sentenceContainer: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginVertical: 4,
    borderRadius: 8,
  },
  currentSentence: {
    backgroundColor: "#FFFFFF",
    borderLeftWidth: 4,
    borderLeftColor: "#007AFF",
  },
  completedSentence: {
    backgroundColor: "transparent",
  },
  sentenceRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  copyButton: {
    padding: 2,
    marginTop: 2,
    width: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  copyButtonText: {
    fontSize: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginTop: 8,
  },
  statusPerfect: {
    backgroundColor: "#2196F3", // 파란색 - 완벽
  },
  statusGood: {
    backgroundColor: "#34C759", // 초록색 - 좋음
  },
  statusIncorrect: {
    backgroundColor: "#FF3B30", // 빨간색 - 틀림
  },
  statusSkipped: {
    backgroundColor: "#8E8E93", // 회색 - 스킵
  },
  sentenceText: {
    flex: 1,
    fontSize: 16,
    color: "#333",
    lineHeight: 24,
  },
  currentSentenceText: {
    fontWeight: "700",
    color: "#000",
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
    fontWeight: "600",
  },
  input: {
    backgroundColor: "#fff",
    borderWidth: 2,
    borderColor: "#e0e0e0",
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: "top",
  },
  inputCorrect: {
    borderColor: "#34C759",
  },
  inputIncorrect: {
    borderColor: "#FF3B30",
  },
  feedbackCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  feedbackCorrect: {
    backgroundColor: "#E8F5E9",
  },
  feedbackPerfect: {
    backgroundColor: "#E8F5E9",
    borderWidth: 2,
    borderColor: "#34C759",
  },
  feedbackGood: {
    backgroundColor: "#FFFBEA",
    borderWidth: 2,
    borderColor: "#FFD60A",
  },
  feedbackIncorrect: {
    backgroundColor: "#FFEBEE",
  },
  feedbackText: {
    fontSize: 14,
    color: "#333",
    lineHeight: 20,
  },
  correctText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#34C759",
    marginBottom: 4,
  },
  correctSubtext: {
    fontSize: 14,
    color: "#666",
  },
  historyContainer: {
    backgroundColor: "#F9F9F9",
    borderRadius: 12,
    marginBottom: 16,
    overflow: "hidden",
  },
  historyHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
  },
  historyLabel: {
    fontSize: 12,
    color: "#999",
    textTransform: "uppercase",
    fontWeight: "600",
  },
  historyToggle: {
    fontSize: 14,
    color: "#999",
  },
  historyContent: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  historyItem: {
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#E0E0E0",
  },
  historyInput: {
    fontSize: 14,
    color: "#333",
    marginBottom: 8,
  },
  historyFeedbackRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  historyResultBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  historyResultPerfect: {
    backgroundColor: "#E3F2FD", // 연한 파란색
  },
  historyResultGood: {
    backgroundColor: "#E8F5E9", // 연한 초록색
  },
  historyResultIncorrect: {
    backgroundColor: "#FFEBEE", // 연한 빨간색
  },
  historyResultText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#333",
  },
  historyFeedback: {
    fontSize: 13,
    color: "#FF3B30",
    lineHeight: 18,
  },
  historyFeedbackPerfect: {
    color: "#2196F3", // 파란색
  },
  historyFeedbackGood: {
    color: "#34C759", // 초록색
  },
  historyCorrect: {
    color: "#34C759",
  },
  buttonContainer: {
    gap: 12,
  },
  actionRow: {
    flexDirection: "row",
    gap: 12,
  },
  button: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  submitButton: {
    backgroundColor: "#007AFF",
  },
  skipButton: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#e0e0e0",
  },
  answerButton: {
    backgroundColor: "#F5F5F5",
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  skipButtonText: {
    color: "#666",
    fontSize: 16,
    fontWeight: "600",
  },
  answerButtonText: {
    color: "#FF9500",
    fontSize: 16,
    fontWeight: "600",
  },
  errorText: {
    fontSize: 16,
    color: "#FF3B30",
  },
});
