<?php
// Receive rows from Magic Scraper's "Send to webhook" and append them to a
// JSON Lines file, one row per line. PHP 8.1 or later, no packages.
//
// Test on your own computer:   MS_SECRET=your-secret php -S localhost:8787 hook.php
// On a server: put this file in your web root and keep MS_FILE outside it.

$secret = getenv('MS_SECRET') ?: '';                                    // the Secret typed in Magic Scraper, if any
$file   = getenv('MS_FILE') ?: dirname(__DIR__) . '/magic-scraper-rows.jsonl'; // outside the web root
$onRows = getenv('ON_ROWS') ?: '';                                      // a script to run with the new rows on stdin

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
$got = $_SERVER['HTTP_X_MAGIC_SCRAPER_SECRET'] ?? '';
if ($secret !== '' && !hash_equals($secret, $got)) { http_response_code(401); exit; }

$msg = json_decode(file_get_contents('php://input'), true);
if (!is_array($msg)) { http_response_code(400); exit; }

// "Batches of rows" (the default) sends an object; "One item per row" a bare list.
$rows = array_is_list($msg) ? $msg : ($msg['rows'] ?? []);
header('Content-Type: application/json');
if (!array_is_list($msg) && ($msg['event'] ?? '') === 'test') { echo '{"ok":true}'; exit; }

$lines = '';
foreach ($rows as $row) $lines .= json_encode($row, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
file_put_contents($file, $lines, FILE_APPEND | LOCK_EX);
echo json_encode(['ok' => true, 'rows' => count($rows)]);

// The rows go to the script on stdin, never on its command line: scraped text
// is written by whoever made the page, and a shell would run it. An array
// command (PHP 7.4+) starts the script without a shell at all.
if ($onRows !== '' && $rows) {
    $p = proc_open([$onRows], [0 => ['pipe', 'r'], 1 => ['file', '/dev/null', 'w'], 2 => ['file', '/dev/null', 'w']], $pipes);
    if (is_resource($p)) { fwrite($pipes[0], $lines); fclose($pipes[0]); proc_close($p); }
}
