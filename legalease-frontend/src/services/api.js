import axios from "axios";

// Real backend client for later
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Mock API for now
export const askLegalQuestion = async (question) => {
  await new Promise((resolve) => setTimeout(resolve, 1400));

  const q = question.toLowerCase();

  if (q.includes("জমি") || q.includes("land")) {
    return {
      question,
      answer: {
        legalExplanation:
          "জমি সংক্রান্ত বিরোধের ক্ষেত্রে প্রথমে মালিকানা সংক্রান্ত নথি, খতিয়ান, নামজারি, পর্চা ও দখলের প্রমাণ সংগ্রহ করা জরুরি। বিরোধের প্রকৃতি অনুযায়ী প্রশাসনিক বা দেওয়ানি আইনি পদক্ষেপ গ্রহণ করা যেতে পারে।",
        userRights:
          "আপনি বৈধ মালিক হলে আপনার সম্পত্তির সুরক্ষা ও পুনরুদ্ধারের আইনি অধিকার রয়েছে। আইন অনুযায়ী অবৈধ দখল বা হস্তক্ষেপের বিরুদ্ধে প্রতিকার চাওয়া সম্ভব।",
        nextSteps: [
          "সমস্ত জমির কাগজপত্র একত্র করুন",
          "স্থানীয় ভূমি অফিস বা সহকারী কমিশনার (ভূমি)-এর সাথে যোগাযোগ করুন",
          "প্রয়োজনে দেওয়ানি আদালতে মামলা দায়েরের বিষয়ে পরামর্শ নিন",
        ],
        formalVersion:
          "উপস্থাপিত তথ্যের ভিত্তিতে প্রতীয়মান হয় যে, জমি সংক্রান্ত বিরোধ নিষ্পত্তির জন্য প্রাসঙ্গিক মালিকানা নথি সংগ্রহপূর্বক যথাযথ কর্তৃপক্ষের নিকট প্রতিকার প্রার্থনা করা সমীচীন হবে।",
      },
      sources: [
        { source: "Land Law", section: "Section 23" },
        { source: "Civil Procedure Code", section: "Section 9" },
      ],
      confidence: 0.82,
      warning: "প্রয়োজনে একজন আইনজীবীর পরামর্শ নিন।",
    };
  }

  if (q.includes("fraud") || q.includes("প্রতারণা")) {
    return {
      question,
      answer: {
        legalExplanation:
          "প্রতারণার ঘটনায় প্রাথমিকভাবে ঘটনার প্রমাণ, লেনদেনের তথ্য, যোগাযোগের রেকর্ড এবং সংশ্লিষ্ট ডকুমেন্ট সংগ্রহ করতে হবে। অপরাধের প্রকৃতি অনুযায়ী ফৌজদারি আইনের অধীনে অভিযোগ দায়ের করা যেতে পারে।",
        userRights:
          "প্রতারণার শিকার ব্যক্তি হিসেবে আপনি থানায় অভিযোগ দায়ের, তদন্তের আবেদন এবং ফৌজদারি প্রতিকারের দাবি করতে পারেন।",
        nextSteps: [
          "প্রমাণ হিসেবে স্ক্রিনশট, রসিদ, মেসেজ বা কল রেকর্ড সংরক্ষণ করুন",
          "নিকটস্থ থানায় অভিযোগ বা জিডি করুন",
          "প্রয়োজনে আইনজীবীর মাধ্যমে ফৌজদারি মামলা করার বিষয় বিবেচনা করুন",
        ],
        formalVersion:
          "উপলব্ধ তথ্যানুসারে প্রতারণাজনিত অপরাধের ক্ষেত্রে উপযুক্ত প্রমাণাদি সংরক্ষণপূর্বক আইনশৃঙ্খলা রক্ষাকারী বাহিনীর নিকট অভিযোগ দায়ের করা যুক্তিসঙ্গত হবে।",
      },
      sources: [
        { source: "Penal Code", section: "Section 420" },
        { source: "Criminal Procedure Code", section: "Section 154" },
      ],
      confidence: 0.88,
      warning: "",
    };
  }

  return {
    question,
    answer: {
      legalExplanation:
        "প্রদত্ত প্রশ্নের ভিত্তিতে নির্দিষ্ট আইনি অবস্থান স্পষ্টভাবে শনাক্ত করা যায়নি।",
      userRights:
        "আপনার অধিকার নির্ধারণের জন্য আরও নির্দিষ্ট তথ্য প্রয়োজন।",
      nextSteps: [
        "ঘটনার সম্পূর্ণ বিবরণ দিন",
        "সংশ্লিষ্ট কাগজপত্র বা তথ্য যোগ করুন",
        "একজন আইনজীবীর পেশাদার পরামর্শ নিন",
      ],
      formalVersion:
        "উপস্থাপিত তথ্য অপর্যাপ্ত হওয়ায় নির্দিষ্ট আইনি মতামত প্রদান করা এই পর্যায়ে সম্ভব নয়।",
    },
    sources: [{ source: "General Legal Reference", section: "N/A" }],
    confidence: 0.46,
    warning: "তথ্য অনিশ্চিত। অনুগ্রহ করে একজন আইনজীবীর পরামর্শ নিন।",
  };
};

// Later for real backend:
//
// export const askLegalQuestion = async (question) => {
//   const response = await API.get("/ask", {
//     params: { q: question },
//   });
//   return response.data;
// };