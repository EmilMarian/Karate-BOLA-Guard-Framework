
package karate;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
import org.junit.jupiter.api.Test;

public class KarateTestRunner {
    @Test
    void testFeatureFile() {
        String featuresPath = "classpath:src/test/resources";

                Results results = Runner.path("classpath:")
                .reportDir("target/karate-reports")
                .outputJunitXml(true)
                .outputCucumberJson(true)
                .parallel(1);
        System.out.println("Scanned feature files: " + results.getFeaturesPassed());

        assert results.getFeaturesFailed() == 0;
    }
}
