# Codex Model Gate Guide

Codex Model Gate organizes tasks run by Codex CLI. It helps you prepare the request, review the recommended model and skills, approve execution, and find the results later.

## Start here

1. In the **Task** tab, choose where projects will be stored.
2. Write what you want to do and, if necessary, use **Attach files...**.
3. Select **Analyze task**. The Gate recommends a model, reasoning level, and skills.
4. Review the decision. You may adjust the skill selection before continuing.
5. Select **Confirm and run**. Files are kept in the task's exclusive folder.
6. When finished, review the result, open the created files, and record their quality.

### Simple mode and task templates

The application opens in **simple mode**, with the essential controls for preparing, analyzing, and running a task. Directly below the description, web research, and attachments are **1. Analyze task** and **2. Confirm and run**, followed by the model, reasoning level, risk, and skill summary. The detailed library and monitoring area appear farther down. Use `Ctrl+Enter` to analyze and `Ctrl+Shift+Enter` to run. Enable **Show advanced options** when you want to choose the policy, model, reasoning level, or skill library, or inspect technical execution details.

The buttons use the interface's existing colors to show progress: **Analyze task** turns blue when a description is ready. After analysis it turns green with a checkmark, and **Confirm and run** turns blue. Once execution is started, the second button also turns green. Changing the description or attachments returns the controls to the preparation state; analyze again before running.
Selecting **Confirm and run** opens the approval dialog over the main window. The Codex CLI version check runs in the background without opening another window.

Under **Start from a template**, choose a starting point for creating a document, analyzing a file, generating an image, researching references, or organizing data. Replace the fields in brackets with your context before analyzing.

## Model and reasoning level

The Gate recommends the main GPT-6 models according to the **complexity of the requested result**, not the number of words in the request. **Luna — Low** handles bounded lookups and transformations, such as a public date or current exchange rate, with an appropriate source when needed. **Sol — Low** handles explicit fact checks; **Sol — Medium/High** handles research, synthesis, creation, specialized judgment, and work with meaningful impact. **Astra — Medium/High** handles broad deliverables with interdependent steps and decisions, with more review for high-impact work. The assessment also shows risk, tool use, specialization, verifiability, and ambiguity. The final model and effort choice remains with the user in advanced options. Legacy models are in the separate **Legacy model** selector for manual use; older Terra records remain supported.

Low, Medium, High, Extra high and Maximum depend on model support. Ultra requires an explicit declaration in the public local catalog for the same CLI version and is not recommended automatically.

Requests to explain how a technical mechanism works, including downconversion and upconversion, receive at least **Sol — Medium** in Portuguese, English, or Spanish. The Gate considers the explanation required even when the question is short.

### Interface responsiveness

When a task completes, the Gate opens the answer before updating files and history. The usage dashboard reuses records already loaded, and the duration estimate uses the same data. The Codex CLI version checked in the current session is reused at authorization, and progress messages are grouped to keep the window responsive. These changes reduce interface delays; model response time still depends on the task, the selected effort, and Codex CLI.

### Usage and estimated cost

For conversations with several responses, the task record lists time and tokens for each execution separately. The **Usage** tab sums the tokens reported by those executions. Older records without this breakdown retain the available total.

After a task runs, the Gate displays the input, cached input, output, and reasoning tokens reported by Codex CLI, plus the estimated cost for the selected model. Costs use two decimal places and the currency associated with the interface language. If the CLI does not report usage, the estimate is unavailable. This is an estimate, not a charge: it excludes tool fees, special modalities, long-context and priority processing, and exchange-rate changes beyond the Gate's reference rate.

Standard text-token reference prices in USD per million tokens, for prompts up to 272K input tokens: GPT-6 Luna, input $0.10, cached input $0.01, output $0.50; GPT-6 Sol, $2, $0.20, and $10; GPT-6 Astra, $10, $1, and $50. Legacy GPT-5.6 Terra remains available for manual selection and retains the rates configured in the Gate: input $2, cached input $0.20, and output $12. Prices can change; see the [official OpenAI pricing table](https://developers.openai.com/api/docs/pricing).

## Skills

Leave automatic selection enabled for the Gate to choose skills related to the task. To choose them yourself, enable **Use manual selection** and search using part of a skill's name; you do not need to type the complete name. Skills shown under **Skills recommended for this task** are the ones that will be used for that task. Removing one from the task does not delete it from the library.

Automatic selection uses Codex CLI with Sol 6.1 — Medium to analyze the request, attachment contents, and the complete skills catalog. Incremental memory stores full descriptions, headings, and scope excerpts, refreshing changed files. AI compares capabilities, chooses complementary skills in execution order, and explains each contribution. New skills participate by scope without registering fixed routes. Catalog size follows the library; duplicate names use the most recently installed version.

Analysis is a model call and consumes tokens. Skill profiles and relevant attachment contents are sent through the authenticated CLI. It runs in the background with a read-only sandbox before execution approval. Text, DOCX, text PDFs, and XLSX have bounded local previews; PNG, JPEG, and WebP are sent as image inputs. AI may read the specified originals when needed. Scanned PDFs or unsupported formats may require OCR or additional readers; limitations must appear in the recommendation.

Review choices, reasons, and limitations before approval. You can cancel analysis or adjust choices manually. CLI failure never counts as completed analysis or silently falls back to fixed rules. Reanalyze changed attachments. Execution records keep the decision and reported analysis tokens separately from task-turn usage. The legacy optional `gate_outcomes` field is readable but not required for intelligent selection.

When using **Schedule task...**, enter the local date and time as `YYYY-MM-DD HH:MM`. The Gate requests your confirmation at the scheduled time.

## Previous tasks and files

In **Previous tasks**, use **Search tasks** to locate an execution by request, topic, response, or file name. Search updates as you type, ignores capitalization and accents, and is also available with `Ctrl+F`. Use the additional filters to restrict results by date, model, status, or skill. Select a task and open **Files** to see only its files. Displayed dates and the date filter use the interface format and local time; the record file keeps its original timestamps for auditing.

The area to the right of search shows only the number of displayed records. Review token and cost totals in **Usage**.

Tasks run by this version preserve the Codex session. Select one and use **Continue conversation** to request adjustments, review the delivery, or continue the analysis in the same session and folder. In **Previous tasks**, all four filters share one row. The action bar shows **Refresh records**, **Continue conversation**, and **Rate record**. **List** contains unrated records and the report; **Open / export** contains text view, TXT/PDF export, and the records folder; **.gate packages** contains task export and import. Every function remains available. The bar stays on one row and scrolls horizontally when needed. The task list and **Selected record details** divide the available height equally. Each new message is added to the task record. Older records without a session identifier remain readable, but cannot retroactively restore context that was not saved.

## Usage

Open **Usage** to review estimated costs and aggregated tokens for today, the last seven days, this month, this year, or all time. Select **Custom** to enter a start and end date in `YYYY-MM-DD` format. Filter by all models or Luna, Terra, Sol, and Astra. The table identifies the model and shows tasks, input, cache, output, reasoning, and cost by hour, day, or month depending on the selected period. English displays dates as `YYYY-MM-DD`, uses commas for thousands, and uses a decimal point for monetary values. Choose the interface-language currency automatically or select USD, BRL, or EUR. Use **Export CSV...** to save the displayed rows for a spreadsheet.

In the **Breakdown** table, headers and values are centered within each column, including model, tokens, and estimated cost.

The notice beside the summary explains that the total is an estimate, not an account charge. The dashboard aggregates local records with token usage and an identifiable model; it shows how many records fall in the period, how many are included, and how many are excluded for missing data. Costs use the prices and reference exchange rate configured in the Gate, have two decimal places, and can be recalculated with current rates: records store the model and tokens, not an invoice or the price in effect when the task ran.

## Links in responses

Page addresses shown in a response appear as blue, underlined hyperlinks. Select one to open it in the default Windows browser. The Gate recognizes both plain URLs and titled Markdown links, and only opens valid `http` or `https` addresses.

## Controlled web research

For public dates, election polls, or tasks using the reliable sources skill, the Gate enables Codex live web search. The task starts directly in Codex, which can consult current sources and cite their links. Check dates and figures against the original source before relying on them.

Technical mechanism explanations also enable live web search. For every task, the Gate instructs Codex to open each cited page, confirm that it directly supports the claim, and use a specific section when possible. This rule applies automatically. Verification depends on access to the page during execution; if access fails, Codex should state the limitation instead of inventing a citation.

Select **Allow Gate visual browser (Edge)** to make a visible, isolated browser available to Codex. Checking the box does not start a search: the task starts in Codex, and Edge opens only if Codex chooses the browser tool. The session does not automatically reuse your personal logins or history. Without the box checked, **Edge search terms (optional)** is disabled and has no effect on the task.

This field accepts **search words**, for example `Mexico election calendar 2027`. They are a suggestion, not a command: Codex may use different terms or may not use Edge. If left blank, the task description is sent as the suggested query. When used, the visual browser searches Google and Bing and can open a page only if it appears among the search results. Pasting `https://example.com/article` into this field searches for that URL as text; it **does not open the page directly**. To request analysis of a specific link, put it in the main task description, for example `Read and summarize https://example.com/article`. Codex can try to access the page with the available tools and should say if it cannot. Bounded questions about election or sports competition dates receive Luna — Low and live web search; requests for comparison or analysis are rated by the complexity of the result.

When enabled, the Gate offers its visual browser to Codex through local MCP tools. Codex live web search works independently of this option.

## Response screen

When a task finishes, the Gate automatically opens **Response**, including in simple mode. The technical panel remains limited to advanced options, but you never need to enable it merely to read the final response.

## Backup and data

Use **Create backup...** in the Task tab to save projects, skills, records, and settings in a ZIP file. New backups use a compact internal structure to avoid Windows long-path errors. The `backup-manifest.json` file inside the ZIP maps each item to its original path.

### Full ZIP backup and `.gate` task package

The **full ZIP backup** and the **`.gate` package** serve different purposes. The ZIP created with **Create backup...** contains Gate data: projects, the skill library, records, and settings. Use it for a general backup or to migrate these data to another computer. To restore it, select **Restore backup...**, choose the ZIP, and review the file and category preview. Choose **Yes** to replace files that match the backup; **No** to preserve current files and restore items under alternate names; **Cancel** to stop. Files outside the backup are never removed. Restoring settings from another computer may require restarting the Gate.

The **`.gate` package** contains only one selected task: its record and files in its task folder, such as attachments and outputs. It does not include the full library, settings, or other projects and records. In **Previous tasks**, select the task and choose **Export task as package...**. On the other installation, choose **Import `.gate` package...**. The Gate restores the files in a dedicated folder and creates a local record. Then analyze the imported task to start a new conversation with that context. The package does not transfer the authenticated session or original conversation identifier, so it cannot resume the previous session. It can also serve as an isolated portable copy of one task.

To migrate to another computer, install and open the Gate, then select **Restore backup...**. Choose the ZIP copied from the previous computer. If the new computer has no data, choose **Yes** to restore normally. If it already contains data you want to preserve, choose **No**: the Gate keeps current files and adds restored files with a restoration suffix.

Application data is stored in a dedicated Gate folder. **Open Gate data** displays that folder in File Explorer. Normal application updates preserve this data.

## Codex CLI

The Gate needs Codex CLI installed and authenticated to run tasks. The **Codex CLI** area shows its status and provides installation instructions. The Gate looks for the executable both on PATH and in the Windows Codex app installation. You can still analyze and organize a task without the CLI, but you cannot run it. **Decision ready** means analysis is complete and execution still needs approval; it does not mean the model has answered. After **2. Confirm and run**, watch for **Codex started** and open **Response** when it finishes. If the CLI cannot be found, the task does not start and the screen explains why.

If preparation or the interface fails, the Gate shows an error instead of leaving the task waiting indefinitely. For diagnosis, open the task folder and read `.codex-model-gate/startup-status.txt`; interface errors are also recorded in `gui-error.txt`. Creating a folder or confirming approval alone does not prove that Codex started.

Version 2.6.5 corrects the start and duration clock. After approving a new task or continuing a conversation, look for **Codex started** before treating the process as started.

The Gate identifies the installed CLI version. Sol 6.1 (`gpt-6.1-sol`) requires CLI 0.159.1 or later; previous Sol 6 and Luna require 0.156.1 or later. Use **Official download / update** to open the official installation and update instructions, then **Check again**. **Check for new releases** reads the official changelog when clicked, without downloading or running installers. The public local CLI catalog supplements available models when it matches the identified version. Model access also depends on the account and workspace. Rejections display diagnostics; the Gate preserves the authorized model.

## Language

Use **Language** at the top of the Task tab. The choice is saved in Gate settings, included in backups, and stored on the drive in the portable edition. Changing the language restarts the application to load the complete interface consistently. The interface language does not automatically change the language of your task or Codex response.

## Tips

- State a clear desired result, for example: “create a PDF report with these sections.”
- Review attachments, skills, and destination folder before approval.
- If Codex asks a question, use **Answer pending question** to keep the same task and context.
- The Gate does not delete files produced when an execution is cancelled; open the task folder to review what was already created.


## Version 2.7 changes

Analyze, run, and cancel remain in the bottom bar while scrolling. Simple mode collapses detailed library and technical controls. Cards distinguish recommended and selected models. Controls wrap with window width; tables scroll horizontally and history has an adjustable divider. Copy or export the response and open diagnostics directly. Language changes are blocked during activity; the request and available local attachments are saved as a draft on exit.

Preparation, attachment copying, history loading, skill indexing, import/export, backups, and document validation use background jobs. Responses appear before history refresh; files do not open automatically. Cancellation terminates the process tree and preserves partial results. This reduces local stalls; model response time still depends on CLI, network, and task.

Task packages include active attachments and remap outputs to the new workspace. Backups include externally stored managed task folders; restoration remaps paths and does not transfer authenticated sessions. Missing source files cannot be recovered. Restoration without replacement keeps Markdown records readable with the `.md` extension. CLI credentials are excluded from packages and backups. Local writes are atomic, retain the previous revision, and surface failures.

Usage is grouped by each turn date. New turns preserve reference pricing and exchange rates; **Recalculate with current prices and exchange rates** is optional. Older records without turn metrics use the available total and date, and current reference prices where historical pricing is absent. Old Sol records retain previous Sol 6. Reasoning levels are filtered by model; Ultra appears only when declared by the matching public local CLI catalog.

Automatic opening is optional, off by default, and limited to three PDFs/images after successful validation and saving.
