use aho_corasick::{AhoCorasick, MatchKind};
use deunicode::deunicode;
use linkify::{LinkFinder, LinkKind};
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::{
    collections::{HashMap, HashSet},
    fmt::Write,
    fs::File,
    io::{BufRead, BufReader},
};
use symspell::{SymSpell, UnicodeStringStrategy};
use unicode_blocks::find_unicode_block;
use unicode_normalization::UnicodeNormalization;
use unicode_properties::{GeneralCategoryGroup, UnicodeGeneralCategory};
use unicode_segmentation::UnicodeSegmentation;

const NOT_ALLOWED_CATEGORIES: [char; 1] = ['C'];

const ALLOWED_BLOCKS: [&str; 7] = [
    "Latin",
    "Greek",
    "Phonetic",
    "Spacing",
    "General Punctuation",
    "Currency Symbols",
    "IPA",
];
const VIETNAMESE_ALLOWED_CHARS: [char; 178] = [
    'A', 'a', 'Á', 'á', 'À', 'à', 'Ả', 'ả', 'Ã', 'ã', 'Ạ', 'ạ', 'Ă', 'ă', 'Ắ', 'ắ', 'Ằ', 'ằ', 'Ẳ',
    'ẳ', 'Ẵ', 'ẵ', 'Ặ', 'ặ', 'Â', 'â', 'Ấ', 'ấ', 'Ầ', 'ầ', 'Ẩ', 'ẩ', 'Ẫ', 'ẫ', 'Ậ', 'ậ', 'B', 'b',
    'C', 'c', 'D', 'd', 'Đ', 'đ', 'E', 'e', 'É', 'é', 'È', 'è', 'Ẻ', 'ẻ', 'Ẽ', 'ẽ', 'Ẹ', 'ẹ', 'Ê',
    'ê', 'Ế', 'ế', 'Ề', 'ề', 'Ể', 'ể', 'Ễ', 'ễ', 'Ệ', 'ệ', 'G', 'g', 'H', 'h', 'I', 'i', 'Í', 'í',
    'Ì', 'ì', 'Ỉ', 'ỉ', 'Ĩ', 'ĩ', 'Ị', 'ị', 'K', 'k', 'L', 'l', 'M', 'm', 'N', 'n', 'O', 'o', 'Ó',
    'ó', 'Ò', 'ò', 'Ỏ', 'ỏ', 'Õ', 'õ', 'Ọ', 'ọ', 'Ô', 'ô', 'Ố', 'ố', 'Ồ', 'ồ', 'Ổ', 'ổ', 'Ỗ', 'ỗ',
    'Ộ', 'ộ', 'Ơ', 'ơ', 'Ớ', 'ớ', 'Ờ', 'ờ', 'Ở', 'ở', 'Ỡ', 'ỡ', 'Ợ', 'ợ', 'P', 'p', 'Q', 'q', 'R',
    'r', 'S', 's', 'T', 't', 'U', 'u', 'Ú', 'ú', 'Ù', 'ù', 'Ủ', 'ủ', 'Ũ', 'ũ', 'Ụ', 'ụ', 'Ư', 'ư',
    'Ứ', 'ứ', 'Ừ', 'ừ', 'Ử', 'ử', 'Ữ', 'ữ', 'Ự', 'ự', 'V', 'v', 'X', 'x', 'Y', 'y', 'Ý', 'ý', 'Ỳ',
    'ỳ', 'Ỷ', 'ỷ', 'Ỹ', 'ỹ', 'Ỵ', 'ỵ',
];

pub static EMOTICONS: Lazy<HashMap<String, String>> = Lazy::new(|| {
    let emoticons_filepath = "data/emojis/combined_emoji_vi.json";
    let file = File::open(emoticons_filepath).unwrap();
    let reader = BufReader::new(file);
    let emoticons_json: HashMap<String, String> = serde_json::from_reader(reader).unwrap();
    emoticons_json
        .iter()
        .filter_map(|(emoticon, emoticon_name)| {
            if emoticon.chars().all(|c| c.is_ascii_alphabetic()) {
                return None;
            }
            Some((emoticon.to_owned(), format!(" {} ", emoticon_name)))
        })
        .collect()
});

pub static UNICODE_EMOJIS: Lazy<HashMap<String, String>> = Lazy::new(|| {
    let emoticons_filepath = "data/emojis/unicode_emoji_vi.json";
    let file = File::open(emoticons_filepath).unwrap();
    let reader = BufReader::new(file);
    let emoticons_json: HashMap<String, String> = serde_json::from_reader(reader).unwrap();
    emoticons_json
});

const BIGRAM_DUPLICATE_THRESHOLD: f32 = 0.3; // magic number
const SEGMENTATION_MAX_EDIT_DISTANCE: i64 = 2;

pub static SYMSPELL: Lazy<SymSpell<UnicodeStringStrategy>> = Lazy::new(|| {
    eprintln!("Spelling Corrector: SymSpell loading...");
    let mut spell = SymSpell::default();
    let vietnamese_frequency_filepath = "data/dictionaries/vietnamese/vi_50k.txt";
    spell.load_dictionary(&vietnamese_frequency_filepath, 0, 1, " ");
    spell
});

pub static SYMSPELL_WITHOUT_ACCENTS: Lazy<SymSpell<UnicodeStringStrategy>> = Lazy::new(|| {
    eprintln!("Spelling Corrector: SymSpell (without accents) loading...");
    let mut spell = SymSpell::default();
    let vietnamese_frequency_filepath = "data/dictionaries/vietnamese/vi_50k_no_accent.txt";
    spell.load_dictionary(&vietnamese_frequency_filepath, 0, 1, " ");
    spell
});

static VIETNAMESE_DICTIONARY: Lazy<HashSet<String>> = Lazy::new(|| {
    eprintln!("Spelling Corrector: Vietnamese dictionary loading...");
    let mut dictionary: HashSet<String> = HashSet::new();
    let vietnamese_dictionary_filepath = "data/dictionaries/vietnamese/words_alpha.txt";
    let file = File::open(vietnamese_dictionary_filepath).unwrap();
    let reader = BufReader::new(file);
    for line in reader.lines() {
        dictionary.insert(line.unwrap());
    }
    dictionary
});

static VIETNAMESE_SWEAR_WORDS: Lazy<Vec<String>> = Lazy::new(|| {
    eprintln!("Spelling Corrector: Vietnamese swear words loading...");
    let mut swear_words: HashSet<String> = HashSet::new();
    let vietnamese_swear_words_filepath = "data/dictionaries/vietnamese/vi.json";
    let file = File::open(vietnamese_swear_words_filepath).unwrap();
    let reader = BufReader::new(file);
    let s_words: Vec<String> = serde_json::from_reader(reader).unwrap();
    swear_words.extend(s_words);

    let vietnamese_swear_words_filepath = "data/dictionaries/vietnamese/vn_offensive_words.txt";
    let file = File::open(vietnamese_swear_words_filepath).unwrap();
    let reader = BufReader::new(file);
    for line in reader.lines() {
        let word = line.unwrap();
        if word.chars().nth(0).unwrap() != '#' {
            swear_words.insert(word);
        }
    }
    swear_words.into_iter().collect::<Vec<String>>()
});

static VIETNAMESE_SWEAR_WORDS_REPLACEMENT: Lazy<Vec<String>> = Lazy::new(|| {
    eprintln!("Spelling Corrector: Vietnamese swear words replacement creating...");
    VIETNAMESE_SWEAR_WORDS
        .clone()
        .into_iter()
        // .filter(|word| !word.contains(" "))
        .map(|word| format!(" {} ", word))
        .collect()
});

// ----------------------------------------------------------------------------
pub fn aho_corasick_replace_all(
    text: &str,
    replacement_hashmap: &HashMap<String, String>,
) -> String {
    let patterns = replacement_hashmap
        .clone()
        .into_keys()
        .collect::<Vec<String>>();
    let replace_with = replacement_hashmap
        .clone()
        .into_values()
        .collect::<Vec<String>>();
    let ac = AhoCorasick::builder()
        .ascii_case_insensitive(true)
        .match_kind(MatchKind::LeftmostLongest)
        .build(patterns)
        .unwrap();
    ac.replace_all(&text, &replace_with)
}

pub fn apply<'a, F>(line: &'a str, mut f: F) -> String
where
    F: FnMut(&'a str, &mut String),
{
    let mut buf = String::new();
    f(line, &mut buf);
    buf
}

// ----------------------------------------------------------------------------
pub fn replace_emails(text: &str, output: &mut String) {
    let mut finder = LinkFinder::new();
    finder.kinds(&[LinkKind::Email]);

    let emails = finder
        .links(&text)
        .into_iter()
        .map(|link| link.as_str())
        .collect::<Vec<&str>>();
    let emails_replacement = vec![" (email) "; emails.len()];

    let ac = AhoCorasick::builder()
        .ascii_case_insensitive(true)
        .match_kind(MatchKind::LeftmostLongest)
        .build(&emails)
        .unwrap();
    let result = ac.replace_all(&text, &emails_replacement);
    write!(output, "{}", result).unwrap();
}

pub fn replace_urls(text: &str, output: &mut String) {
    let mut finder = LinkFinder::new();
    finder.kinds(&[LinkKind::Url]);
    finder.url_must_have_scheme(false);

    let links = finder
        .links(&text)
        .into_iter()
        .map(|link| link.as_str())
        .collect::<Vec<&str>>();
    let links_replacement = vec![" (url) "; links.len()];

    let ac = AhoCorasick::builder()
        .ascii_case_insensitive(true)
        .match_kind(MatchKind::LeftmostLongest)
        .build(&links)
        .unwrap();
    let result = ac.replace_all(&text, &links_replacement);
    write!(output, "{}", result).unwrap();
}

pub fn unicode_normalize(text: &str, output: &mut String) {
    let result = text.nfkc().collect::<String>();
    write!(output, "{}", result).unwrap();
}

pub fn get_unicode_block(letter: &char) -> &str {
    find_unicode_block(*letter).unwrap().name()
}

pub fn get_unicode_category(letter: &char) -> char {
    match letter.general_category_group() {
        GeneralCategoryGroup::Letter => 'L',
        GeneralCategoryGroup::Mark => 'M',
        GeneralCategoryGroup::Number => 'N',
        GeneralCategoryGroup::Punctuation => 'P',
        GeneralCategoryGroup::Symbol => 'S',
        GeneralCategoryGroup::Separator => 'Z',
        GeneralCategoryGroup::Other => 'C',
    }
}

pub fn replace_emoticons(text: &str, output: &mut String) {
    let result = aho_corasick_replace_all(text, &EMOTICONS);
    write!(output, "{}", result).unwrap();
}

pub fn replace_unicode_emojis(text: &str, output: &mut String) {
    let result = aho_corasick_replace_all(text, &UNICODE_EMOJIS);
    write!(output, "{}", result).unwrap();
}

pub fn unicode_filter_by_blocks(text: &str, output: &mut String) {
    let result = text
        .chars()
        .filter(|letter| {
            ALLOWED_BLOCKS
                .iter()
                .any(|allowed_block| get_unicode_block(letter).contains(allowed_block))
        })
        .collect::<String>();
    write!(output, "{}", result).unwrap();
}

pub fn unicode_filter_by_categories(text: &str, output: &mut String) {
    let result = text
        .chars()
        .filter(|letter| !NOT_ALLOWED_CATEGORIES.contains(&get_unicode_category(letter)))
        .collect::<String>();
    write!(output, "{}", result).unwrap();
}

pub fn unicode_decode(text: &str, output: &mut String) {
    let result = deunicode(text);
    write!(output, "{}", result).unwrap();
}

pub fn unicode_decode_vietnamese(text: &str, output: &mut String) {
    let mut new_chars = Vec::new();
    for char in text.chars() {
        if VIETNAMESE_ALLOWED_CHARS.contains(&char) {
            new_chars.push(char.to_string());
        } else {
            new_chars.push(deunicode(&char.to_string()));
        }
    }
    let result = new_chars.join("");
    write!(output, "{}", result).unwrap();
}

// ----------------------------------------------------------------------------
fn split_bigram(word: &str) -> Vec<[char; 2]> {
    let letters = word.chars().into_iter().collect::<Vec<char>>();
    let letters0 = letters.split_last().unwrap().1;
    let letters1 = letters.split_first().unwrap().1;
    let mut bigrams = Vec::new();
    for (letter0, letter1) in letters0.iter().zip(letters1) {
        let bigram = [*letter0, *letter1];
        bigrams.push(bigram);
    }
    bigrams
}

fn join_bigram(bigrams: &Vec<[char; 2]>) -> String {
    let mut new_word = String::new();
    for bigram in bigrams.iter() {
        new_word.push(bigram[0]);
    }
    new_word.push(bigrams.last().unwrap()[1]);
    new_word
}

fn reduce_bigram(word: &str) -> String {
    let bigrams = split_bigram(word);
    let mut new_bigrams: Vec<[char; 2]> = Vec::new();
    let mut repeat_flag = false;
    let mut duplication_num = 0;
    for bigram in bigrams.iter() {
        if bigram[0] == bigram[1] {
            if repeat_flag {
                continue;
            }
            repeat_flag = true;
            duplication_num += 1;
        } else {
            repeat_flag = false;
        }
        new_bigrams.push(*bigram);
    }
    let len_bigrams = new_bigrams.len() + 1;
    if len_bigrams > 3 && duplication_num as f32 > len_bigrams as f32 * BIGRAM_DUPLICATE_THRESHOLD {
        let mut new_new_bigrams: Vec<[char; 2]> = Vec::new();
        for bigram in new_bigrams.iter() {
            if bigram[0] == bigram[1] {
                continue;
            }
            new_new_bigrams.push(*bigram);
        }
        return join_bigram(&new_new_bigrams);
    }
    join_bigram(&new_bigrams)
}

fn is_in_corpora(word: &str) -> bool {
    VIETNAMESE_DICTIONARY.contains(word)
}

fn is_a_number(word: &str) -> bool {
    match word.parse::<f64>() {
        Ok(_) => true,
        Err(_) => false,
    }
}

fn is_math_equation(word: &str) -> bool {
    word.chars()
        .into_iter()
        .all(|letter| ['N', 'S', 'P'].contains(&get_unicode_category(&letter)))
}

fn is_punctuations_or_symbols(word: &str) -> bool {
    word.chars()
        .into_iter()
        .all(|letter| ['P', 'S'].contains(&get_unicode_category(&letter)))
}

fn word_segmentation_without_accents(text: &str, spell: &str) -> String {
    let c_text = text.graphemes(true).collect::<Vec<&str>>();
    let indices = spell
        .match_indices(' ')
        .map(|(i, _)| i)
        .collect::<Vec<usize>>();
    let mut result: Vec<String> = Vec::new();
    let mut last_index = 0;
    for (i, index) in indices.iter().enumerate() {
        result.push(c_text[last_index..(index - i)].join(""));
        last_index = index - i;
    }
    result.push(c_text[last_index..].join(""));
    result.join(" ")
}

pub fn correct_unknown_word(word: &str) -> String {
    let mut new_word = word
        .chars()
        .map(|letter| {
            if ['L', 'N'].contains(&get_unicode_category(&letter)) {
                letter
            } else {
                ' '
            }
        })
        .collect::<String>();
    //? single word?
    new_word.retain(|letter| !letter.is_whitespace()); //?
    new_word = reduce_bigram(&new_word);

    let ac = AhoCorasick::builder()
        .ascii_case_insensitive(true)
        .match_kind(MatchKind::LeftmostLongest)
        .build(&VIETNAMESE_SWEAR_WORDS.to_owned())
        .unwrap();
    new_word = ac.replace_all(&new_word, &VIETNAMESE_SWEAR_WORDS_REPLACEMENT);

    let spell0 = SYMSPELL_WITHOUT_ACCENTS.word_segmentation(
        &apply(&new_word, unicode_decode),
        SEGMENTATION_MAX_EDIT_DISTANCE,
    );
    let spell1 = SYMSPELL.word_segmentation(&new_word, SEGMENTATION_MAX_EDIT_DISTANCE);
    if spell0.segmented_string == apply(&spell1.segmented_string, unicode_decode) {
        return spell1.segmented_string;
    }

    if spell0.distance_sum < spell1.distance_sum {
        return word_segmentation_without_accents(&new_word, &spell0.segmented_string);
    } else if spell0.distance_sum > spell1.distance_sum {
        return spell1.segmented_string;
    } else if spell0.prob_log_sum < spell1.prob_log_sum {
        return word_segmentation_without_accents(&new_word, &spell0.segmented_string);
    } else if spell0.prob_log_sum > spell0.prob_log_sum {
        return spell1.segmented_string;
    } else {
        return spell1.segmented_string;
    }
}

pub fn process_text(text: &str, output: &mut String) {
    let mut result_words: Vec<String> = Vec::new();
    for word in text.split_whitespace().into_iter() {
        let word = word.to_lowercase();
        if is_a_number(&word) {
            result_words.push(word);
            continue;
        }
        if is_punctuations_or_symbols(&word) {
            result_words.push(word);
            continue;
        }
        if is_math_equation(&word) {
            result_words.push(word);
            continue;
        }
        if is_in_corpora(&word) {
            result_words.push(word);
            continue;
        }
        if is_in_corpora(&word) {
            result_words.push(word);
            continue;
        }
        result_words.push(correct_unknown_word(&word));
    }
    let result = result_words.join(" ");
    write!(output, "{}", result).unwrap();
}

// ----------------------------------------------------------------------------
#[pyfunction]
fn process(text: &str) -> PyResult<String> {
    let mut new_text = text.to_owned();
    new_text = new_text.trim().to_lowercase();
    new_text = apply(&new_text, unicode_normalize);
    new_text = apply(&new_text, replace_emails);
    new_text = apply(&new_text, replace_urls);
    new_text = apply(&new_text, replace_emoticons);
    new_text = apply(&new_text, replace_unicode_emojis);
    new_text = apply(&new_text, unicode_filter_by_blocks);
    new_text = apply(&new_text, unicode_filter_by_categories);
    new_text = apply(&new_text, unicode_decode_vietnamese);
    new_text = apply(&new_text, process_text);
    Ok(new_text)
}

/// A Python module implemented in Rust.
#[pymodule]
fn text_profanity_process(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process, m)?)?;
    Ok(())
}
