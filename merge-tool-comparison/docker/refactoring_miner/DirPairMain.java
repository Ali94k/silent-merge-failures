// Thin wrapper around RefactoringMiner's detectAtDirectories API.
// Emits a single JSON document on stdout describing every refactoring
// detected between two directory snapshots.
//
// Usage: java -cp <wrapper>:<RM-lib>/* DirPairMain <leftDir> <rightDir>
// Output schema:
//   {"directories":{"left":"...","right":"..."},
//    "refactorings":[<Refactoring.toJSON()>, ...]}
// Exit codes:
//   0 — success (output JSON valid; refactorings array may be empty)
//   1 — usage error, missing dir, or RefactoringMiner exception (fail-closed)

import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class DirPairMain {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: DirPairMain <leftDir> <rightDir>");
            System.exit(1);
        }
        File left = new File(args[0]);
        File right = new File(args[1]);
        if (!left.isDirectory() || !right.isDirectory()) {
            System.err.println("Both arguments must be existing directories: "
                + left + ", " + right);
            System.exit(1);
        }

        final List<String> jsonParts = new ArrayList<>();
        final boolean[] errored = new boolean[]{false};

        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();
        miner.detectAtDirectories(left.toPath(), right.toPath(), new RefactoringHandler() {
            @Override
            public void handle(String commitId, List<Refactoring> refactorings) {
                for (Refactoring r : refactorings) {
                    jsonParts.add(r.toJSON());
                }
            }

            @Override
            public void handleException(String commitId, Exception e) {
                errored[0] = true;
                e.printStackTrace(System.err);
            }
        });

        if (errored[0]) {
            System.err.println("RefactoringMiner reported an exception during detection.");
            System.exit(1);
        }

        StringBuilder sb = new StringBuilder();
        sb.append("{\"directories\":{\"left\":\"").append(escape(left.getAbsolutePath()))
          .append("\",\"right\":\"").append(escape(right.getAbsolutePath()))
          .append("\"},\"refactorings\":[");
        for (int i = 0; i < jsonParts.size(); i++) {
            sb.append(jsonParts.get(i));
            if (i < jsonParts.size() - 1) sb.append(",");
        }
        sb.append("]}");
        System.out.println(sb.toString());
    }

    private static String escape(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
