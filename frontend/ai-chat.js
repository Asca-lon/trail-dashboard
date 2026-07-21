const AI_CHAT_MAX_LENGTH = 500;
const AI_CHAT_RESPONSE_DELAY = 650;

const AI_CHAT_PAGE_CONFIG = {
  "dashboard.html": {
    contextFallback: "메인 대시보드",
    contextSelector: null,
    suggestions: [
      "현재 위험도가 가장 높은 구간은?",
      "우선 점검 대상을 요약해줘",
      "현재 필터 조건을 설명해줘",
    ],
    answer: "현재 화면의 위험 구간, 역별 위험도와 우선 점검 목록을 기준으로 확인했습니다. 실제 RAG API 연결 전이므로 지금은 화면 동작을 확인하기 위한 예시 답변입니다.",
  },
  "station-detail.html": {
    contextFallback: "역 상세",
    contextSelector: "[data-station-detail-name]",
    formatContext: (value) => `${value.replace(/\s*상세$/, "")} 상세`,
    suggestions: [
      "이 역의 지연률이 높은 이유는?",
      "가장 영향이 큰 특보는?",
      "평상시와 특보 발생 시 차이는?",
    ],
    answer: "현재 역 상세 화면의 지연 지표와 특보별 영향 데이터를 기준으로 확인했습니다. 실제 원인 분석 결과는 RAG API 연결 후 제공됩니다.",
  },
  "route-detail.html": {
    contextFallback: "구간 상세",
    contextSelector: "[data-route-detail-from-station], [data-route-detail-to-station]",
    formatContext: (_, elements) => {
      const names = elements.map((element) => element.textContent.trim()).filter(Boolean);
      return names.length === 2 ? `${names[0]} → ${names[1]} 구간` : "구간 상세";
    },
    suggestions: [
      "이 구간이 위험한 이유는?",
      "현재 상태와 과거 사례를 비교해줘",
      "우선 확인할 항목은?",
    ],
    answer: "현재 구간의 위험도, 지연 변화와 과거 유사 사례를 기준으로 확인했습니다. 실제 비교 분석은 RAG API 연결 후 제공됩니다.",
  },
};

function getAIChatPageName() {
  return window.location.pathname.split("/").pop() || "dashboard.html";
}

function getAIChatConfig() {
  return AI_CHAT_PAGE_CONFIG[getAIChatPageName()] || AI_CHAT_PAGE_CONFIG["dashboard.html"];
}

function createAIChatMarkup() {
  const root = document.createElement("div");
  root.className = "ai-chat";
  root.innerHTML = `
    <aside class="ai-chat__drawer" id="ai-chat-drawer" role="dialog" aria-modal="false" aria-labelledby="ai-chat-title" aria-describedby="ai-chat-subtitle" data-ai-chat-drawer data-state="closed" hidden>
      <header class="ai-chat__header">
        <div class="ai-chat__heading">
          <div class="ai-chat__title-row">
            <h2 class="ai-chat__title" id="ai-chat-title">AI 어시스턴트</h2>
            <span class="ai-chat__badge">BETA</span>
          </div>
          <p class="ai-chat__subtitle" id="ai-chat-subtitle">현재 화면의 데이터를 기반으로 답변합니다.</p>
        </div>
        <div class="ai-chat__header-actions">
          <button class="ai-chat__icon-button" type="button" aria-label="AI 채팅 최소화" data-ai-chat-minimize><span class="ai-chat__icon ai-chat__icon--minus" aria-hidden="true"></span></button>
          <button class="ai-chat__icon-button" type="button" aria-label="AI 채팅 닫기" data-ai-chat-close><span class="ai-chat__icon ai-chat__icon--close" aria-hidden="true"></span></button>
        </div>
      </header>
      <section class="ai-chat__context" aria-labelledby="ai-chat-context-label">
        <p class="ai-chat__context-label" id="ai-chat-context-label">현재 분석 화면</p>
        <p class="ai-chat__context-title" data-ai-chat-context>메인 대시보드</p>
      </section>
      <section class="ai-chat__messages" aria-label="AI 채팅 메시지" aria-live="polite" aria-busy="false" data-ai-chat-messages>
        <div class="ai-chat__empty-state" data-ai-chat-empty>
          <span class="ai-chat__empty-icon" aria-hidden="true"></span>
          <h3>현재 화면에 대해 질문해보세요</h3>
          <p>화면에 표시된 수치와 분석 결과를 기준으로 답변합니다.</p>
        </div>
        <ol class="ai-chat__message-list" data-ai-chat-message-list></ol>
        <div class="ai-chat__loading" data-ai-chat-loading hidden>
          <span class="ai-chat__loading-dots" aria-hidden="true"><i></i><i></i><i></i></span>
          <span>답변을 생성하고 있습니다.</span>
        </div>
        <section class="ai-chat__status ai-chat__status--error" data-ai-chat-error hidden>
          <span class="ai-chat__status-icon ai-chat__status-icon--error" aria-hidden="true"></span>
          <div><h3>답변을 불러오지 못했습니다.</h3><p>잠시 후 다시 시도해 주세요.</p><button type="button" data-ai-chat-retry>다시 시도</button></div>
        </section>
        <section class="ai-chat__status ai-chat__status--no-data" data-ai-chat-no-data hidden>
          <span class="ai-chat__status-icon ai-chat__status-icon--no-data" aria-hidden="true"></span>
          <div><h3>현재 화면에 분석 가능한 데이터가 없습니다.</h3><p>다른 역이나 구간을 선택한 후 다시 질문해 주세요.</p></div>
        </section>
      </section>
      <section class="ai-chat__suggestions" aria-labelledby="ai-chat-suggestions-title">
        <h3 class="sr-only" id="ai-chat-suggestions-title">추천 질문</h3>
        <div class="ai-chat__suggestion-list" data-ai-chat-suggestions></div>
      </section>
      <form class="ai-chat__composer" data-ai-chat-form>
        <label class="sr-only" for="ai-chat-question">AI 어시스턴트에게 질문하기</label>
        <div class="ai-chat__input-row">
          <textarea class="ai-chat__textarea" id="ai-chat-question" name="question" maxlength="${AI_CHAT_MAX_LENGTH}" rows="2" placeholder="궁금한 내용을 질문하세요..." data-ai-chat-input></textarea>
          <button class="ai-chat__send-button" type="submit" aria-label="질문 보내기" data-ai-chat-send disabled><span class="ai-chat__icon ai-chat__icon--send" aria-hidden="true"></span></button>
        </div>
        <div class="ai-chat__composer-meta"><span data-ai-chat-count>0 / ${AI_CHAT_MAX_LENGTH}</span><span>AI 답변은 참고용으로 활용해 주세요.</span></div>
      </form>
    </aside>`;
  return root;
}

function createAIChatTrigger() {
  const button = document.createElement("button");
  button.className = "ai-chat__trigger";
  button.type = "button";
  button.setAttribute("aria-label", "AI 어시스턴트 열기");
  button.setAttribute("aria-controls", "ai-chat-drawer");
  button.setAttribute("aria-expanded", "false");
  button.dataset.aiChatTrigger = "";
  button.innerHTML = '<span class="ai-chat__icon ai-chat__icon--bot" aria-hidden="true"></span>';
  return button;
}

function initializeAIChat() {
  const headerInner = document.querySelector(".site-header__inner, .station-global-header__inner");
  if (!headerInner) return;

  const config = getAIChatConfig();
  const trigger = createAIChatTrigger();
  const headerActions = document.createElement("div");
  headerActions.className = "global-header__actions";
  headerActions.append(trigger);
  headerInner.append(headerActions);

  const root = createAIChatMarkup();
  document.body.append(root);

  const drawer = root.querySelector("[data-ai-chat-drawer]");
  const input = root.querySelector("[data-ai-chat-input]");
  const sendButton = root.querySelector("[data-ai-chat-send]");
  const messages = root.querySelector("[data-ai-chat-messages]");
  const messageList = root.querySelector("[data-ai-chat-message-list]");
  const emptyState = root.querySelector("[data-ai-chat-empty]");
  const loadingState = root.querySelector("[data-ai-chat-loading]");
  const errorState = root.querySelector("[data-ai-chat-error]");
  const noDataState = root.querySelector("[data-ai-chat-no-data]");
  const characterCount = root.querySelector("[data-ai-chat-count]");
  let lastQuestion = "";
  let responseTimer = null;

  function updateContext() {
    const contextElements = config.contextSelector
      ? [...document.querySelectorAll(config.contextSelector)]
      : [];
    const firstValue = contextElements[0]?.textContent.trim() || config.contextFallback;
    const context = config.formatContext
      ? config.formatContext(firstValue, contextElements)
      : config.contextFallback;
    root.querySelector("[data-ai-chat-context]").textContent = context;
  }

  function setDrawerOpen(isOpen, shouldRestoreFocus = false) {
    if (isOpen) {
      drawer.hidden = false;
      window.requestAnimationFrame(() => drawer.dataset.state = "open");
      trigger.classList.add("ai-chat__trigger--active");
      trigger.setAttribute("aria-expanded", "true");
      updateContext();
      window.setTimeout(() => input.focus(), 220);
      return;
    }
    drawer.dataset.state = "closed";
    trigger.classList.remove("ai-chat__trigger--active");
    trigger.setAttribute("aria-expanded", "false");
    window.setTimeout(() => {
      drawer.hidden = true;
      if (shouldRestoreFocus) trigger.focus();
    }, 180);
  }

  function hideTransientStates() {
    loadingState.hidden = true;
    errorState.hidden = true;
    noDataState.hidden = true;
    messages.setAttribute("aria-busy", "false");
  }

  function appendMessage(role, text) {
    emptyState.hidden = true;
    const item = document.createElement("li");
    item.className = `ai-chat__message ai-chat__message--${role}`;
    const bubble = document.createElement("p");
    bubble.className = "ai-chat__message-bubble";
    bubble.textContent = text;
    const time = document.createElement("time");
    time.className = "ai-chat__message-time";
    time.dateTime = new Date().toISOString();
    time.textContent = new Intl.DateTimeFormat("ko-KR", { hour: "2-digit", minute: "2-digit", hour12: true }).format(new Date());
    item.append(bubble, time);
    messageList.append(item);
    messages.scrollTop = messages.scrollHeight;
  }

  function completeMockResponse(question, isRetry = false) {
    hideTransientStates();
    if (!isRetry && question.includes("오류")) {
      errorState.hidden = false;
    } else if (question.includes("데이터 없음")) {
      noDataState.hidden = false;
    } else {
      appendMessage("assistant", config.answer);
    }
    messages.scrollTop = messages.scrollHeight;
  }

  function submitQuestion(question) {
    const normalizedQuestion = question.trim();
    if (!normalizedQuestion) return;
    lastQuestion = normalizedQuestion;
    hideTransientStates();
    appendMessage("user", normalizedQuestion);
    input.value = "";
    input.dispatchEvent(new Event("input"));
    loadingState.hidden = false;
    messages.setAttribute("aria-busy", "true");
    messages.scrollTop = messages.scrollHeight;
    responseTimer = window.setTimeout(() => completeMockResponse(normalizedQuestion), AI_CHAT_RESPONSE_DELAY);
  }

  const suggestionContainer = root.querySelector("[data-ai-chat-suggestions]");
  config.suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.className = "ai-chat__suggestion";
    button.type = "button";
    button.textContent = suggestion;
    button.addEventListener("click", () => submitQuestion(suggestion));
    suggestionContainer.append(button);
  });

  trigger.addEventListener("click", () => setDrawerOpen(drawer.hidden));
  root.querySelector("[data-ai-chat-minimize]").addEventListener("click", () => setDrawerOpen(false, true));
  root.querySelector("[data-ai-chat-close]").addEventListener("click", () => setDrawerOpen(false, true));
  root.querySelector("[data-ai-chat-form]").addEventListener("submit", (event) => {
    event.preventDefault();
    submitQuestion(input.value);
  });
  root.querySelector("[data-ai-chat-retry]").addEventListener("click", () => {
    hideTransientStates();
    loadingState.hidden = false;
    messages.setAttribute("aria-busy", "true");
    responseTimer = window.setTimeout(() => completeMockResponse(lastQuestion, true), AI_CHAT_RESPONSE_DELAY);
  });
  input.addEventListener("input", () => {
    characterCount.textContent = `${input.value.length} / ${AI_CHAT_MAX_LENGTH}`;
    sendButton.disabled = input.value.trim().length === 0;
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      root.querySelector("[data-ai-chat-form]").requestSubmit();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !drawer.hidden) setDrawerOpen(false, true);
  });

  updateContext();
  if (config.contextSelector) {
    const observer = new MutationObserver(updateContext);
    document.querySelectorAll(config.contextSelector).forEach((element) => {
      observer.observe(element, { childList: true, subtree: true, characterData: true });
    });
  }
}

initializeAIChat();
