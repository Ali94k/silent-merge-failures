# S-D1 Spec Table — Ali's GD1 eyeball

Pooled usable specs: **37/48 = 77.1%** (GD1 machine threshold 80%: FAIL)

> **Final GD1 verdict: GD1 PASS** — plan §12 Amendment 2 (Ali, 2026-07-16, failure-path option b): design targets reduced to file-local shapes (declaration visible within the unit's intersecting files); re-scored **37/39**. Decomposition + ids: `gd1_machine.json`.

| detector | units | usable |
|---|---|---|
| D1 | 21 | 21 |
| D2 | 14 | 8 |
| D3 | 13 | 8 |

Quote-provenance grades over all checked sites: {'exact': 91, 'empty': 14, 'normalized': 3}

| unit | det | status | usable | extraction summary |
|---|---|---|---|---|
| `apache_commons-collections__84e70353ad` | D1 | ok | ✓  | import `fail` removed by theirs; 3 usage site(s), added by ours |
| `ardesco_selenium-standalone-server-plugin__957d978135` | D2 | ok | ✓  | return_type_changed+param_type_changed; arity_changed=no by theirs; decl_visible=yes; 4 call site(s); Theirs retyped getBinaryFilenames() to return List<String> (and typed the local filenamesW |
| `atam4j_atam4j__71fcecb071` | D1 | ok | ✓  | import `PassingTest` replaced by ours; 1 usage site(s), added by theirs |
| `buddycloud_buddycloud-server-java__48e4675ee2` | D2 | partial | ✓  | param_added; arity_changed=yes by ours; decl_visible=no; 1 call site(s); THEIRS-added test rsmStillAddedWhenThereAreNoResults stubs getNodeItemReplies with 4 args  |
| `cloudfoundry_cf-java-client__80d0a0dff9` | D2 | partial | ✗ old_sig=missing/absent new_sig=missing/absent call_sites=ok | name_and_signature+return_type_changed; arity_changed=no by ours; decl_visible=no; 2 call site(s); The theirs-added update() method calls the old Reactor value-mapping API Mono.then(Functio |
| `cloudfoundry_cf-java-client__a9d35d542d` | D2 | partial | ✗ old_sig=ok new_sig=ok call_sites=none-verify | param_added; arity_changed=yes by theirs; decl_visible=yes; 0 call site(s); OURS refactored list() to build a 4-element tuple (getApplicationNames, getDomainName, Mon |
| `cternes_openkeepass__bb53512ab2` | D1 | ok | ✓  | import `Group` removed by theirs; 2 usage site(s), added by ours |
| `datastax_java-driver__e1535e89ad` | D3 | ok | ✓  | field removed by ours; 1 ref site(s); rm2=no joern=no |
| `dius_java-faker__9f0019116a` | D1 | ok | ✓  | import `isEmptyOrNullString` narrowed by ours; 1 usage site(s), added by theirs |
| `dtrules_dtrules__505c5cbf82` | D1 | ok | ✓  | import `RulesDirectory` removed by ours; 1 usage site(s), added by theirs |
| `elisarver_selophane__4ecc600017` | D3 | partial | ✗ decl=missing/absent refs=ok verdicts=ok missed_shape=ok | class relocated by theirs; 1 ref site(s); rm2=no joern=no |
| `feroult_yawp__141f79a8e9` | D1 | ok | ✓  | import `List` removed by ours; 2 usage site(s), added by theirs |
| `gitools_gitools__02221bf3d8` | D3 | partial | ✗ decl=missing/absent refs=ok verdicts=ok missed_shape=ok | class relocated by ours; 1 ref site(s); rm2=no joern=no |
| `gwtbootstrap3_gwtbootstrap3__5c0d1eab79` | D3 | ok | ✓  | class removed by ours; 2 ref site(s); rm2=no joern=no |
| `imixs_imixs-workflow__23b86de5b4` | D3 | ok | ✓  | other relocated by ours; 2 ref site(s); rm2=no joern=no |
| `javaparser_javaparser__41a398414f` | D2 | partial | ✗ old_sig=missing/absent new_sig=missing/absent call_sites=ok | return_type_changed; arity_changed=no by theirs; decl_visible=no; 1 call site(s); OURS's new toMethodUsage calls getTypeDeclaration().getAllMethods() treating the result as |
| `javaparser_javaparser__dc6254f1bf` | D3 | ok | ✓  | method removed by ours; 1 ref site(s); rm2=no joern=no |
| `jcabi_jcabi-github__b13d2596ba` | D3 | ok | ✓  | method removed by ours; 2 ref site(s); rm2=no joern=no |
| `jcabi_jcabi-github__e18a8ffd16` | D2 | ok | ✓  | param_added+exceptions_changed; arity_changed=yes by ours; decl_visible=yes; 1 call site(s); canFetchAllHooks (added by theirs) calls repo() with 0 args, but ours replaced repo() with |
| `jdeparser_jdeparser2__868afefbb4` | D3 | partial | ✗ decl=ok refs=none-verify verdicts=ok missed_shape=ok | method removed by ours; 0 ref site(s); rm2=no joern=no |
| `jenkinsci_build-timeout-plugin__daeab4a1ee` | D1 | ok | ✓  | import `Nonnull` replaced by theirs; 1 usage site(s), added by ours |
| `jenkinsci_credentials-plugin__e9cf377a17` | D1 | partial | ✓  | import `ArrayList` removed by ours; 1 usage site(s), added by theirs |
| `jline_jline2__5acfe59453` | D3 | ok | ✓  | field renamed by ours; 2 ref site(s); rm2=uncertain joern=no |
| `jmrozanec_cron-utils__a77c0476c3` | D1 | ok | ✓  | import `DAY_OF_YEAR` narrowed by theirs; 2 usage site(s), added by ours |
| `jnr_jnr-unixsocket__467698b6bd` | D1 | ok | ✓  | import `Struct` narrowed by ours; 3 usage site(s), added by theirs |
| `joel-costigliola_assertj-core__df351133a9` | D1 | partial | ✓  | import `failBecauseExpectedAssertionErrorWasNotThrown` removed by ours; 4 usage site(s), added by kept-from-base |
| `logstash_log4j-jsonevent-layout__ee90110799` | D1 | ok | ✓  | import `PatternLayout` narrowed by theirs; 2 usage site(s), added by ours |
| `mercadopago_sdk-java__9dfc950fd2` | D2 | ok | ✓  | exceptions_changed; arity_changed=no by theirs; decl_visible=yes; 3 call site(s); New overloads added by ours declare only 'throws MPException' but delegate to methods whos |
| `mikera_vectorz__d93ef1b341` | D1 | ok | ✓  | import `Random` removed by theirs; 1 usage site(s), added by ours |
| `mitre_http-proxy-servlet__b7a68118f2` | D2 | ok | ✓  | return_type_changed+other; arity_changed=no by ours; decl_visible=yes; 2 call site(s); getTargetUri() (added by theirs) declares return type URI but returns field targetUri, whi |
| `movsim_movsim__6dae25caf7` | D1 | ok | ✓  | import `MovsimInputLoader` removed by theirs; 1 usage site(s), added by kept-from-base |
| `msopentech_azure-activedirectory-library-for-java__d3f143872b` | D2 | partial | ✗ old_sig=missing/absent new_sig=missing/absent call_sites=ok | param_added; arity_changed=yes by theirs; decl_visible=no; 1 call site(s); passes 6 args to the AuthenticationResult constructor, but theirs' updated signature takes |
| `ninjaframework_ninja__94b2365be3` | D1 | ok | ✓  | import `Cookie` removed by ours; 1 usage site(s), added by theirs |
| `openpnp_openpnp__b62c0ce826` | D3 | partial | ✗ decl=missing/absent refs=ok verdicts=ok missed_shape=ok | method other by ours; 2 ref site(s); rm2=no joern=no |
| `qcadoo_mes__c6cb8180e5` | D3 | partial | ✗ decl=missing/absent refs=ok verdicts=ok missed_shape=ok | method renamed by ours; 1 ref site(s); rm2=no joern=no |
| `sander2798_enderstone__9d0d7b7ba8` | D1 | ok | ✓  | import `RegionSet` removed by theirs; 2 usage site(s), added by ours |
| `sandergielisse_enderstone__df0826f63b` | D2 | partial | ✗ old_sig=missing/absent new_sig=missing/absent call_sites=ok | param_added; arity_changed=yes by theirs; decl_visible=no; 1 call site(s); passes 1 arg (message), new constructor takes 2 args (message, byte); developer fix change |
| `sandergielisse_enderstone__febdb02eb3` | D2 | ok | ✓  | param_added; arity_changed=yes by ours; decl_visible=yes; 6 call site(s); passes 3 args to ItemStack(short,byte,short), but ours changed the constructor to arity 4  |
| `segmentio_analytics-java__0d4a7b4e69` | D1 | partial | ✓  | import `BlockingQueue` removed by theirs; 1 usage site(s), added by kept-from-base |
| `softinstigate_restheart__98dda32101` | D3 | ok | ✓  | parameter renamed by theirs; 3 ref site(s); rm2=yes joern=no |
| `softinstigate_restheart__dc14776b02` | D1 | ok | ✓  | import `DataLoaderDispatcherInstrumentation` removed by theirs; 4 usage site(s), added by ours |
| `sonarsource_sonar-findbugs__b2fd863305` | D2 | partial | ✓  | param_removed+param_type_changed+other; arity_changed=yes by ours; decl_visible=no; 4 call site(s); theirs-added test methods call executor.execute(false, false) with two boolean args, but o |
| `square_javapoet__d019b6f624` | D1 | ok | ✓  | import `ArrayList` replaced by ours; 1 usage site(s), added by theirs |
| `thenewcircle_spring-hibernate-20120924__7ec9c1b4bb` | D1 | ok | ✓  | import `Contact` removed by theirs; 5 usage site(s), added by ours |
| `tumblr_jumblr__31bd6f8335` | D1 | ok | ✓  | import `JsonElement` removed by ours; 2 usage site(s), added by theirs |
| `urbanairship_java-library__bbe0297a10` | D2 | partial | ✗ old_sig=missing/absent new_sig=missing/absent call_sites=ok | param_type_changed; arity_changed=no by unclear; decl_visible=no; 2 call site(s); testNamedUserFullPayload passes a Map<String, String> to addAllPropertyEntries whose param |
| `winder_universal-g-code-sender__c93fec43ee` | D2 | ok | ✓  | return_type_changed; arity_changed=no by ours; decl_visible=yes; 1 call site(s); OURS changed getProcessor's return type to Optional<CommandProcessor> and wrapped every re |
| `yandex-qatools_postgresql-embedded__6e15a53c7e` | D3 | ok | ✓  | field removed by ours; 1 ref site(s); rm2=no joern=no |
